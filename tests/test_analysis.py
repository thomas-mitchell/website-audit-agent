import json

from auditor.nodes.analysis import analyse_page
from auditor.models.findings import Finding, Severity, VerificationStatus


def test_analyse_page(tmp_path):
    analysis_files = {}

    for category in ("accessibility", "seo", "ux"):
        path = tmp_path / f"{category}.json"

        path.write_text(
            json.dumps({
                "category": category,
                "summary": "Test summary",
                "findings": [
                    {
                        "title": f"Test {category} issue",
                        "severity": "medium",
                        "status": "confirmed",
                        "description": "A test issue was detected.",
                        "impact": "Users may experience difficulties.",
                        "recommendation": "Fix the test issue.",
                        "evidence": ["Test evidence"],
                        "reproduction_steps": [
                            "Open the test page.",
                            "Inspect the affected element."
                        ],
                        "references": ["WCAG 2.1.1"]
                    }
                ]
            }),
            encoding="utf-8"
        )

        analysis_files[category] = str(path)

    state = {
        "analysis_files": analysis_files
    }

    result = analyse_page(state)

    # One finding from each of the three analysis files
    assert len(result["findings"]) == 3

    # Findings should remain structured Pydantic objects
    assert all(isinstance(f, Finding) for f in result["findings"])

    # Verify all three categories were aggregated
    titles = {f.title for f in result["findings"]}

    assert titles == {
        "Test accessibility issue",
        "Test seo issue",
        "Test ux issue"
    }

    # Verify the fields were preserved correctly
    for finding in result["findings"]:
        assert finding.severity == Severity.MEDIUM
        assert finding.status == VerificationStatus.CONFIRMED
        assert finding.description == "A test issue was detected."
        assert finding.recommendation == "Fix the test issue."
        assert finding.evidence == ["Test evidence"]
        assert finding.reproduction_steps == [
            "Open the test page.",
            "Inspect the affected element."
        ]
        assert finding.references == ["WCAG 2.1.1"]