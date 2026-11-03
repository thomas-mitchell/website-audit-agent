import json

from auditor.models.findings import Finding, Severity, VerificationStatus
from auditor.models.investigation import (
    InvestigationResult,
    ScreenshotEvidence,
)
from auditor.nodes.report import generate_report


def test_report_includes_screenshot_references(tmp_path):
    page_path = tmp_path / "page.json"
    page_path.write_text(
        json.dumps({
            "title": "Example Website",
            "status_code": 200,
        }),
        encoding="utf-8",
    )

    finding = Finding(
        title="Logo missing alternative text",
        severity=Severity.MEDIUM,
        status=VerificationStatus.CONFIRMED,
        description="The logo image has an empty alt attribute.",
        impact="Screen reader users may miss the brand identity.",
        recommendation="Add descriptive alternative text.",
    )

    investigation = InvestigationResult(
        finding_title=finding.title,
        question="What does the logo depict?",
        answer="The image contains the company logo.",
        evidence=["The image was visually inspected."],
        resolved=True,
        screenshots=[
            ScreenshotEvidence(
                path="runs/test/evidence/screenshots/logo.png",
                capture_type="element",
                selector="img.logo",
                analysed=True,
                analysis_question="What does this image depict?",
                analysis_answer="The image contains the company logo.",
            ),
        ],
    )

    state = {
        "url": "https://example.com",
        "evidence_files": {"page": str(page_path)},
        "findings": [finding],
        "investigation_results": [investigation],
    }

    result = generate_report(state)
    report = result["report"]

    assert "Visual Evidence:" in report
    assert "runs/test/evidence/screenshots/logo.png" in report
    assert "Capture type: element" in report
    assert "Visually analysed: Yes" in report
    assert "The image contains the company logo." in report