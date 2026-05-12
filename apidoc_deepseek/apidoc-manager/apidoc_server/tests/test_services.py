"""Service layer tests."""

import pytest
from apidoc_server.services.diff_service import DiffService
from apidoc_server.services.validation_service import ValidationService


class TestValidationService:
    @pytest.mark.asyncio
    async def test_validate_valid_spec(self, sample_spec):
        service = ValidationService()
        result = await service.validate(sample_spec)
        assert result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_validate_invalid_spec(self):
        service = ValidationService()
        result = await service.validate({"openapi": "3.0.3", "info": {"title": "Invalid API"}, "paths": {}})
        assert result["valid"] is False


class TestDiffService:
    def test_compare_identical(self, sample_spec):
        service = DiffService()
        result = service.compare(sample_spec, sample_spec)
        assert result["summary"]["total_changes"] == 0
    
    def test_compare_with_changes(self, sample_spec):
        import copy
        spec2 = copy.deepcopy(sample_spec)
        spec2["paths"]["/users"]["delete"] = {"summary": "Delete user", "responses": {"204": {"description": "Deleted"}}}
        service = DiffService()
        result = service.compare(sample_spec, spec2)
        assert result["summary"]["total_changes"] > 0
