from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class DecayModel(BaseModel):
    lambda_: float = Field(..., alias="lambda")
    pinned: bool

    class Config:
        populate_by_name = True


class MetadataModel(BaseModel):
    source: str
    content_hash: str


class SpecifySchema(BaseModel):
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
