"""Pydantic schemas for the REST API."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class SpecCreate(BaseModel):
    name:        str            = Field(..., min_length=1, max_length=255)
    description: str            = Field("", max_length=2000)
    content:     dict[str, Any]

class SpecVersionCreate(BaseModel):
    version:   str            = Field(..., min_length=1, max_length=50)
    content:   dict[str, Any]
    changelog: str            = Field("", max_length=2000)

class SpecResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:              int
    name:            str
    description:     str
    latest_version:  str
    versions_count:  int
    created_at:      datetime
    updated_at:      datetime
    content:         Optional[dict[str, Any]] = None

class SpecListResponse(BaseModel):
    items: list[SpecResponse]
    total: int; page: int; limit: int; pages: int

class DiffRequest(BaseModel):
    version1: str; version2: str

class ImportRequest(BaseModel):
    url: str
