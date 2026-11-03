import json

from auditor.models.findings import Finding, Severity, VerificationStatus
from auditor.nodes.analysis import analyse_page
from auditor.nodes.review import normalise_reviewed_findings


def make_finding(title: str) -> Finding:
    return Finding(
        title=title,
        severity=Severity.MEDIUM,
        status=VerificationStatus.CONFIRMED,
        description="Test description",
        impact="Test impact",
        recommendation="Test recommendation",
    )


def test_analysis_assigns_unique_finding_ids(tmp_path):
    from auditor.models.findings import AnalysisResult

    analysis = AnalysisResult(
        category="accessibility",
        summary="Test",
        findings=[
            make_finding("Finding A"),
            make_finding("Finding B"),
        ],
    )

    path = tmp_path / "accessibility.json"
    path.write_text(
        analysis.model_dump_json(),
        encoding="utf-8",
    )

    result = analyse_page({
        "analysis_files": {
            "accessibility": str(path)
        }
    })

    findings = result["findings"]

    assert len(findings) == 2
    assert findings[0].id
    assert findings[1].id
    assert findings[0].id != findings[1].id

    for finding in findings:
        assert finding.source_ids == [finding.id]


def test_review_preserves_id_when_title_changes():
    original = make_finding("Images may lack alt text")
    original.id = "finding-123"
    original.source_ids = ["finding-123"]

    reviewed = original.model_copy(deep=True)
    reviewed.title = "Site logo missing alt text"

    result = normalise_reviewed_findings(
        [reviewed],
        [original],
    )

    assert result[0].id == "finding-123"
    assert result[0].source_ids == ["finding-123"]


def test_merged_finding_retains_source_ids():
    first = make_finding("Unnamed logo link")
    first.id = "finding-1"
    first.source_ids = ["finding-1"]

    second = make_finding("Missing logo alt text")
    second.id = "finding-2"
    second.source_ids = ["finding-2"]

    merged = make_finding("Logo accessibility issues")
    merged.id = "finding-1"
    merged.source_ids = ["finding-1", "finding-2"]

    result = normalise_reviewed_findings(
        [merged],
        [first, second],
    )

    assert result[0].id == "finding-1"
    assert result[0].source_ids == [
        "finding-1",
        "finding-2",
    ]