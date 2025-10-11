"""Pydantic models for data validation."""
from pydantic import BaseModel


class Requirement(BaseModel):
    """Schema for requirement documents."""

    priority: str
    component: str
    user_story: str
    acceptance: str
