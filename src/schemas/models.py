"""Pydantic models for data validation."""

from datetime import datetime
from typing import List, Literal, Optional

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


class TestCase(BaseModel):
    """Individual test case within a test spec."""

    name: str
    description: str
    type: Literal["unit", "integration", "e2e", "performance", "security"]
    priority: Literal["critical", "high", "medium", "low"]


class TestSpec(BaseModel):
    """Test specification schema - defines what to test and how."""

    type: Literal["TestSpec"] = Field(default="TestSpec", frozen=True)
    session_id: str
    scope: str = Field(..., description="Feature/component/module being tested")
    method: Literal[
        "unit", "integration", "e2e", "performance", "security", "acceptance"
    ] = Field(..., description="Testing methodology")
    coverage_target: str = Field(
        ...,
        description="Target coverage: percentage (e.g., '85%') or delta (e.g., '+2%')",
    )
    test_cases: Optional[list[TestCase]] = Field(
        default=None, description="Detailed list of test cases to implement"
    )
    tools: Optional[list[str]] = Field(
        default=None,
        description="Testing frameworks/tools to use (e.g., pytest, vitest, playwright)",
    )
    preconditions: Optional[list[str]] = Field(
        default=None, description="Setup requirements before tests can run"
    )
    success_criteria: Optional[list[str]] = Field(
        default=None, description="Conditions for test suite success"
    )
    component: Optional[str] = Field(
        default=None, description="Component/module name for filtering"
    )


class ExecSpec(BaseModel):
    """Execution specification for agent-driven tasks."""

    working_dir: str = Field(..., description="Directory where commands are executed")
    commands: list[str] = Field(
        ..., description="Allowed shell commands the agent can run"
    )
    artifacts: list[str] = Field(
        ..., description="Files the agent is expected to create/modify"
    )
    env: list[str] = Field(
        ..., description="Required environment variable names (not values)"
    )
    approval_required: bool = Field(
        ..., description="Whether human approval is needed before execution"
    )
    entry_task: Optional[str] = Field(
        default=None, description="Initial command or instruction to start with"
    )
    constraints: Optional[list[str]] = Field(
        default=None, description="Execution constraints or guidelines"
    )


class Task(BaseModel):
    """Executable work unit schema."""

    type: Literal["Task"] = Field(default="Task", frozen=True)
    session_id: str
    status: Literal["open", "in_progress", "blocked", "review", "done"] = Field(
        ..., description="Current task status"
    )
    component: str = Field(..., description="Component/module being modified")
    est_time: str = Field(
        ..., description="Estimated time to complete (e.g., '2h', '30m', '1d')"
    )
    assignee: Optional[str] = Field(
        default=None, description="User ID or agent name assigned"
    )
    executor: Optional[Literal["human", "claude-code"]] = Field(
        default=None, description="Who/what executes this task"
    )
    priority: Optional[Literal["critical", "high", "medium", "low"]] = Field(
        default=None, description="Task priority"
    )
    exec_spec: Optional[ExecSpec] = Field(
        default=None, description="Required if executor is claude-code or another agent"
    )
    blockers: Optional[list[str]] = Field(
        default=None, description="Issues preventing task completion"
    )
    dependencies: Optional[list[str]] = Field(
        default=None, description="Task IDs that must complete first"
    )
    acceptance_criteria: Optional[list[str]] = Field(
        default=None, description="Conditions that define task completion"
    )


class Tasks(BaseModel):
    test_spec: TestSpec
    task: Task
    type: Literal["Tasks"] = Field(default="Tasks", frozen=True)
