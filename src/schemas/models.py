"""Pydantic models for data validation."""

from datetime import datetime

from pydantic import BaseModel


class Requirement(BaseModel):
    """Schema for requirement documents."""

    priority: str
    component: str
    user_story: str
    acceptance: str


class ADR(BaseModel):
    """Architecture Decision Record schema."""

    status: str
    date: datetime
    decision: str
    context: str
    consequences: str


class DesignHigh(BaseModel):
    """System/diagram level design schema."""

    components: list[str]
    dependencies: list[str]


class DesignLow(BaseModel):
    """Module/API level design schema."""

    module: str
    interface: str
    data_flows: str


class Threat(BaseModel):
    """Security/reliability threat schema."""

    risk_level: str
    mitigation: str
    component: str


class Plan(BaseModel):
    adr: ADR
    design_high: DesignHigh
    design_low: DesignLow
    threat: Threat
