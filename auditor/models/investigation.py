from enum import Enum
from pydantic import BaseModel, Field

from auditor.models.findings import Finding


class InvestigationType(str, Enum):
    ELEMENT = "element"
    ANCHOR = "anchor"
    ACCESSIBILITY = "accessibility"
    INTERACTION = "interaction"
    VISUAL = "visual"

class InvestigationRequest(BaseModel):
    finding_title: str = Field(
        description="Title of the finding requiring investigation"
    )

    investigation_type: InvestigationType = Field(
        description="Type of investigation required"
    )

    question: str = Field(
        description="Specific question the investigation should answer"
    )

    target: str = Field(
        description="CSS selector, URL, fragment identifier, or element description"
    )

class InvestigationResult(BaseModel):
    finding_title: str = Field(
        description="Title of the finding being investigated"
    )

    question: str = Field(
        description="The original investigation question"
    )

    answer: str = Field(
        description="Evidence-based answer to the investigation question"
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Concrete observations collected using browser tools"
    )

    resolved: bool = Field(
        description="Whether the investigation produced enough evidence to answer the question"
    )

class ReviewResult(BaseModel):
    summary: str = Field(
        description="Summary of the consolidated findings"
    )

    findings: list[Finding] = Field(
        default_factory=list,
        description="Consolidated and validated findings"
    )

    investigations: list[InvestigationRequest] = Field(
        default_factory=list,
        description="Questions requiring additional browser investigation"
    )