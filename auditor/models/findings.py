from enum import Enum
import json
from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VerificationStatus(str, Enum):
    CONFIRMED = "confirmed"
    POTENTIAL = "potential"
    NEEDS_REVIEW = "needs_review"


class Finding(BaseModel):
    title: str = Field(
        description="Short, descriptive title identifying the specific issue"
    )

    severity: Severity = Field(
        description="Severity of the issue based on its impact"
    )

    status: VerificationStatus = Field(
        description=(
            "CONFIRMED: Directly demonstrated by supplied evidence. "
            "POTENTIAL: Evidence suggests an issue but does not prove it. "
            "NEEDS_REVIEW: Requires additional investigation."
        )
    )

    description: str = Field(
        description=(
            "Detailed explanation of the issue, including what is wrong "
            "and why it occurs, where supported by evidence"
        )
    )

    impact: str = Field(
        description=(
            "Specific consequences for affected users, including "
            "accessibility, usability, performance or discoverability"
        )
    )

    recommendation: str = Field(
        description=(
            "Specific, actionable remediation instructions. "
            "Include HTML, CSS or JavaScript examples where useful."
        )
    )

    evidence: list[str] = Field(
        default_factory=list,
        description=(
            "Concrete supporting evidence, such as DOM selectors, "
            "HTML snippets, axe violations or Lighthouse results"
        )
    )

    reproduction_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Steps to reproduce the issue using the available evidence. "
            "Leave empty if the issue cannot be reproduced from the evidence."
        )
    )

    references: list[str] = Field(
        default_factory=list,
        description=(
            "Relevant standards or documentation references, "
            "such as WCAG success criteria. Do not invent references."
        )
    )


class AnalysisResult(BaseModel):
    category: str = Field(
        description="Category of the analysis"
    )

    summary: str = Field(
        description="Brief overall assessment"
    )

    findings: list[Finding] = Field(
        default_factory=list
    )

    @field_validator("findings", mode="before")
    @classmethod
    def parse_findings(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value