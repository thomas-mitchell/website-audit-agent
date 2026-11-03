import asyncio
from pathlib import Path

from auditor.nodes.investigation import investigate_findings
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationResult,
    InvestigationType,
)


def test_investigation_uses_run_screenshot_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    request = InvestigationRequest(
        finding_title="Test finding",
        investigation_type=InvestigationType.VISUAL,
        question="What does the image show?",
        target="#test-image",
    )

    async def mock_investigate(url, request, output_dir=None):
        assert url == "https://example.com"
        assert output_dir == (
            Path("runs")
            / "test-run"
            / "evidence"
            / "screenshots"
        )

        return InvestigationResult(
            finding_title=request.finding_title,
            question=request.question,
            answer="The image contains a test logo.",
            evidence=["Visual inspection identified a logo."],
            resolved=True,
        )

    monkeypatch.setattr(
        "auditor.nodes.investigation.investigate",
        mock_investigate,
    )

    state = {
        "url": "https://example.com",
        "run_id": "test-run",
        "investigations": [request],
    }

    result = asyncio.run(investigate_findings(state))

    assert len(result["investigation_results"]) == 1
    assert result["investigation_results"][0].resolved is True

    output_path = (
        tmp_path
        / "runs"
        / "test-run"
        / "analysis"
        / "investigations.json"
    )

    assert output_path.exists()