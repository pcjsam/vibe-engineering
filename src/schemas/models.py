"""Pydantic models for data validation."""

from datetime import datetime
from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """Schema for requirement documents."""

    type: Literal["Requirement"] = Field(default="Requirement", frozen=True)
    session_id: str
    priority: str
    component: str
    user_story: str
    acceptance: str
    embeddings: Optional[List[float]] = None


class ADR(BaseModel):
    """Architecture Decision Record schema."""

    type: Literal["ADR"] = Field(default="ADR", frozen=True)
    session_id: str
    status: str
    date: datetime
    decision: str
    context: str
    consequences: str


class DesignHigh(BaseModel):
    """System/diagram level design schema."""

    type: Literal["DesignHigh"] = Field(default="DesignHigh", frozen=True)
    session_id: str
    components: list[str]
    dependencies: list[str]


class DesignLow(BaseModel):
    """Module/API level design schema."""

    type: Literal["DesignLow"] = Field(default="DesignLow", frozen=True)
    session_id: str
    module: str
    interface: str
    data_flows: str


class Threat(BaseModel):
    """Security/reliability threat schema."""

    type: Literal["Threat"] = Field(default="Threat", frozen=True)
    session_id: str
    risk_level: str
    mitigation: str
    component: str


class Plan(BaseModel):
    type: Literal["Plan"] = Field(default="Plan", frozen=True)
    session_id: str
    adr: ADR
    design_high: DesignHigh
    design_low: DesignLow
    threat: Threat
