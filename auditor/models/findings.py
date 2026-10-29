from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    title: str = Field(
        description="Short, descriptive title of the issue"
    )

    severity: Severity = Field(
        description="Severity of the issue"
    )

    description: str = Field(
        description="Explanation of the issue and its impact"
    )

    recommendation: str = Field(
        description="Specific, actionable recommendation"
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Evidence supporting the finding"
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