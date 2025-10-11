"""Pydantic models for data validation."""
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class DecayModel(BaseModel):
    """Model for memory decay parameters."""

    lambda_: float = Field(..., alias="lambda")
    pinned: bool

    class Config:
        populate_by_name = True


class MetadataModel(BaseModel):
    """Model for memory metadata."""

    source: str
    content_hash: str


class SpecifySchema(BaseModel):
    """Schema for specification/memory documents."""

    memory_id: str
    project_id: str
    created_at: str  # ISO 8601 datetime string
    author: str
    kind: str
    title: str
    content: str
    tags: List[str]
    deps: List[str]
    priority: float
    decay: DecayModel
    metadata: MetadataModel
    embedding: Optional[List[float]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
