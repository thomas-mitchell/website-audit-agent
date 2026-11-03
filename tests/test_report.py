import json
import asyncio
import base64
from pathlib import Path

from auditor.models.findings import Finding, Severity, VerificationStatus
from auditor.models.investigation import (
    InvestigationResult,
    ScreenshotEvidence,
)
from auditor.nodes.report import generate_report


def test_report_saves_markdown_with_screenshot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    page_path = tmp_path / "page.json"
    page_path.write_text(
        json.dumps({
            "title": "Example Website",
            "status_code": 200,
        }),
        encoding="utf-8",
    )

    screenshot_path = (
        tmp_path
        / "runs"
        / "test-run"
        / "evidence"
        / "screenshots"
        / "logo.png"
    )
    screenshot_path.parent.mkdir(parents=True)

    # A valid 1×1 PNG for testing.
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
        "AAAAC0lEQVR42mP8/x8AAwMCAO+/lXcAAAAASUVORK5CYII="
    )

    screenshot_path.write_bytes(png_data)

    finding = Finding(
        id="finding-123",
        source_ids=["finding-123"],
        title="Site logo missing alt text",
        severity=Severity.MEDIUM,
        status=VerificationStatus.CONFIRMED,
        description="The logo image has an empty alt attribute.",
        impact="Screen reader users may miss the brand identity.",
        recommendation="Give the logo link an accessible name.",
    )

    investigation = InvestigationResult(
        finding_id="finding-123",
        finding_title="Images may lack alt text",
        question="What does the logo depict?",
        answer="The image contains the company logo.",
        evidence=["Visual inspection identified a logo."],
        resolved=True,
        screenshots=[
            ScreenshotEvidence(
                path=str(screenshot_path),
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
        "run_id": "test-run",
        "evidence_files": {"page": str(page_path)},
        "findings": [finding],
        "investigation_results": [investigation],
    }

    result = asyncio.run(generate_report(state))

    report_path = (
        tmp_path / "runs" / "test-run" / "reports" / "audit.md"
    )

    assert report_path.exists()

    markdown = report_path.read_text(encoding="utf-8")

    assert result["report"] == markdown
    assert "# Website Quality Audit" in markdown
    assert "## Executive Summary" in markdown
    assert "| Medium | 1 |" in markdown
    assert "### 1. Site logo missing alt text" in markdown
    assert "#### Investigation" in markdown
    assert "The image contains the company logo." in markdown

    # Screenshot is linked using a path relative to audit.md.
    assert (
        "![Investigation screenshot]"
        "(../evidence/screenshots/logo.png)"
    ) in markdown

    # The investigation is associated by ID despite its old title.
    assert "## Additional Investigation Evidence" not in markdown