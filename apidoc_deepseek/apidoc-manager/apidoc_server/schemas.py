"""Pydantic schemas for API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SpecificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: Dict[str, Any]
    format: str = Field(default="json", pattern="^(json|yaml)$")
    tags: Optional[List[str]] = None
    changelog: Optional[str] = None
    created_by: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def validate_openapi_version(cls, v):
        if "openapi" not in v and "swagger" not in v:
            raise ValueError("Invalid OpenAPI specification")
        return v


class SpecificationResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str] = None
    version: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class SpecificationDetailResponse(SpecificationResponse):
    content: Optional[Dict[str, Any]] = None
    format: Optional[str] = None


class SpecificationListResponse(BaseModel):
    items: List[SpecificationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SpecificationImport(BaseModel):
    url: str
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None


class VersionCreate(BaseModel):
    content: Dict[str, Any]
    version: str
    format: str = "json"
    changelog: Optional[str] = None
    created_by: Optional[str] = None


class VersionResponse(BaseModel):
    id: int
    spec_id: int
    version: str
    format: str
    changelog: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None
    model_config = {"from_attributes": True}


class VersionListResponse(BaseModel):
    items: List[VersionResponse]
    total: int
    page: int
    per_page: int
    pages: int


class DiffRequest(BaseModel):
    version1: str
    version2: str
