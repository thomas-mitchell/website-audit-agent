import json
from auditor.nodes.analysis import analyse_page


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

    result = analyse_page({
        "analysis_files": analysis_files
    })

    assert len(result["findings"]) == 6
    assert any(
        "Fix the test issue." in finding
        for finding in result["findings"]
    )

    assert any(
        "Users may experience difficulties." in finding
        for finding in result["findings"]
    )

    assert any(
        "WCAG 2.1.1" in finding
        for finding in result["findings"]
    )