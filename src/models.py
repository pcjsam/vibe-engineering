from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    repo_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owners: List[str] = []


class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    type: str  # principle, requirement, adr, design-high, design-low, threat, test-spec, task, code-fact, ci-fact
    title: str
    text: str
    fields: Dict[str, Any] = {}
    links: List[str] = []
    tags: List[str] = []
    embedding: Optional[List[float]] = None
    created_by: str = "system"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Edge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    src_id: str
    dst_id: str
    rel: str  # satisfies, implements, tests, supersedes, blocks, duplicates


class Fact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    kind: str
    payload: Dict[str, Any]
    ts: datetime = Field(default_factory=datetime.utcnow)


# Default principles and guidelines for new projects
DEFAULT_PRINCIPLES = [
    {
        "title": "Principle: Clear Requirements",
        "text": "All features must have clearly defined requirements with acceptance criteria before implementation begins.",
        "tags": ["requirements", "clarity", "definition"]
    },
    {
        "title": "Principle: Test-Driven Development",
        "text": "Write tests before implementing functionality. Every feature should have corresponding unit and integration tests.",
        "tags": ["testing", "tdd", "quality"]
    },
    {
        "title": "Principle: Documentation as Code",
        "text": "Keep documentation close to code. ADRs and design decisions should be version controlled and reviewable.",
        "tags": ["documentation", "version-control", "maintainability"]
    },
    {
        "title": "Principle: Security by Design",
        "text": "Consider security implications in every design decision. Conduct threat modeling for new features.",
        "tags": ["security", "threat-modeling", "design"]
    },
    {
        "title": "Principle: Iterative Development",
        "text": "Break large features into smaller, deliverable increments. Prefer working software over comprehensive documentation.",
        "tags": ["agile", "iterative", "delivery"]
    }
]

DEFAULT_GUIDELINES = [
    {
        "title": "Guideline: Architecture Decision Records",
        "text": "Use MADR (Markdown Architecture Decision Records) format for all architectural decisions. Include context, decision, and consequences.",
        "tags": ["adr", "architecture", "decisions"]
    },
    {
        "title": "Guideline: Code Review Process",
        "text": "All code changes require peer review. Reviews should focus on correctness, security, maintainability, and adherence to standards.",
        "tags": ["code-review", "quality", "standards"]
    },
    {
        "title": "Guideline: Naming Conventions",
        "text": "Use clear, descriptive names for variables, functions, and classes. Avoid abbreviations unless they are well-established.",
        "tags": ["naming", "conventions", "readability"]
    },
    {
        "title": "Guideline: Error Handling",
        "text": "Handle errors gracefully with meaningful messages. Log errors appropriately and provide recovery mechanisms where possible.",
        "tags": ["error-handling", "logging", "resilience"]
    },
    {
        "title": "Guideline: Performance Considerations",
        "text": "Consider performance implications early. Profile before optimizing and maintain performance budgets for critical paths.",
        "tags": ["performance", "optimization", "monitoring"]
    }
]