"""Direct tests for spec_service business logic."""
from __future__ import annotations
import json
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from server.models import SpecVersion
from server.schemas import SpecCreate, SpecVersionCreate
from server.services import spec_service

pytestmark = pytest.mark.asyncio

CONTENT = {
    "openapi": "3.1.0",
    "info": {"title": "SvcAPI", "version": "1.0.0"},
    "paths": {"/items": {"get": {"operationId": "list",
                                  "responses": {"200": {"description": "OK"}}}}}
}

class TestCreateSpec:
    async def test_creates_record(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="SvcTest", content=CONTENT))
        assert spec.id is not None and spec.name == "SvcTest"
    async def test_sets_version(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="Versioned", content=CONTENT))
        assert spec.latest_version == "1.0.0"
    async def test_creates_initial_version(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="WithVer", content=CONTENT))
        versions = await spec_service.get_versions(db_session, spec.id)
        assert len(versions) == 1 and versions[0].version == "1.0.0"
    async def test_content_hash_sha256(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="Hashed", content=CONTENT))
        versions = await spec_service.get_versions(db_session, spec.id)
        assert len(versions[0].content_hash) == 64
    async def test_description_stored(self, db_session):
        spec = await spec_service.create_spec(db_session,
            SpecCreate(name="Described", description="desc", content=CONTENT))
        assert spec.description == "desc"

class TestListSpecs:
    async def test_returns_pagination(self, db_session):
        r = await spec_service.list_specs(db_session, 1, 10)
        assert hasattr(r,"items") and hasattr(r,"total") and hasattr(r,"pages")
    async def test_created_spec_in_list(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="Listed", content=CONTENT))
        r = await spec_service.list_specs(db_session, 1, 100)
        assert spec.id in [s.id for s in r.items]
    async def test_limit_respected(self, db_session):
        for i in range(3):
            await spec_service.create_spec(db_session, SpecCreate(name=f"LimTest{i}", content=CONTENT))
        r = await spec_service.list_specs(db_session, 1, 2)
        assert len(r.items) <= 2

class TestGetSpec:
    async def test_returns_existing(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="Gettable", content=CONTENT))
        found = await spec_service.get_spec(db_session, spec.id)
        assert found is not None and found.id == spec.id
    async def test_returns_none_for_missing(self, db_session):
        assert await spec_service.get_spec(db_session, 999999) is None

class TestDeleteSpec:
    async def test_deletes(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="Deletable", content=CONTENT))
        assert await spec_service.delete_spec(db_session, spec.id) is True
        assert await spec_service.get_spec(db_session, spec.id) is None
    async def test_returns_false_missing(self, db_session):
        assert await spec_service.delete_spec(db_session, 999999) is False

class TestSearchSpecs:
    async def test_finds_by_name(self, db_session):
        await spec_service.create_spec(db_session, SpecCreate(name="UniquePaymentService", content=CONTENT))
        r = await spec_service.search_specs(db_session, "UniquePaymentService", 1, 10)
        assert r.total >= 1
    async def test_empty_for_no_match(self, db_session):
        r = await spec_service.search_specs(db_session, "zzz999noway", 1, 10)
        assert r.total == 0 and r.items == []
    async def test_case_insensitive(self, db_session):
        await spec_service.create_spec(db_session, SpecCreate(name="CaseTestUniqueZZZ", content=CONTENT))
        r = await spec_service.search_specs(db_session, "casetestuniquezzz", 1, 10)
        assert r.total >= 1

class TestCreateVersion:
    async def test_creates_version(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="CVTest", content=CONTENT))
        v2c = {**CONTENT, "info":{"title":"T","version":"2.0.0"}}
        sv = await spec_service.create_version(db_session, spec.id,
            SpecVersionCreate(version="2.0.0", content=v2c, changelog="v2"))
        assert sv is not None and sv.version == "2.0.0"
    async def test_updates_latest(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="LatestUp", content=CONTENT))
        v2c = {**CONTENT, "info":{"title":"T","version":"2.0.0"}}
        await spec_service.create_version(db_session, spec.id,
            SpecVersionCreate(version="2.0.0", content=v2c, changelog=""))
        updated = await spec_service.get_spec(db_session, spec.id)
        assert updated.latest_version == "2.0.0"
    async def test_returns_none_missing(self, db_session):
        r = await spec_service.create_version(db_session, 999999,
            SpecVersionCreate(version="1.0",content=CONTENT,changelog=""))
        assert r is None
    async def test_version_count_increases(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="CountTest", content=CONTENT))
        v2c = {**CONTENT, "info":{"title":"T","version":"2.0.0"}}
        await spec_service.create_version(db_session, spec.id,
            SpecVersionCreate(version="2.0.0",content=v2c,changelog=""))
        versions = await spec_service.get_versions(db_session, spec.id)
        assert len(versions) == 2

class TestDiffVersions:
    async def test_diff_same(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="DiffSame", content=CONTENT))
        r = await spec_service.diff_versions(db_session, spec.id, "1.0.0", "1.0.0")
        assert r["summary"]["total"] == 0
    async def test_diff_breaking(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="DiffBreak", content=CONTENT))
        v2c = {"openapi":"3.1.0","info":{"title":"T","version":"2.0.0"},"paths":{}}
        await spec_service.create_version(db_session, spec.id,
            SpecVersionCreate(version="2.0.0",content=v2c,changelog="breaking"))
        r = await spec_service.diff_versions(db_session, spec.id, "1.0.0", "2.0.0")
        assert r["summary"]["breaking"] > 0
    async def test_diff_missing_raises(self, db_session):
        spec = await spec_service.create_spec(db_session, SpecCreate(name="DiffMiss", content=CONTENT))
        with pytest.raises(ValueError, match="not found"):
            await spec_service.diff_versions(db_session, spec.id, "1.0.0", "99.0.0")

class TestSpecVersionModel:
    def test_hash_deterministic(self):
        h1 = SpecVersion.compute_hash(CONTENT); h2 = SpecVersion.compute_hash(CONTENT)
        assert h1 == h2 and len(h1) == 64
    def test_hash_different_content(self):
        assert SpecVersion.compute_hash({"a":1}) != SpecVersion.compute_hash({"b":2})
    def test_get_content_roundtrip(self):
        sv = SpecVersion(content=json.dumps(CONTENT))
        assert sv.get_content() == CONTENT
