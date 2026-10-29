from auditor.nodes.analysis import analyse_page


def test_analyse_page(tmp_path):
    analysis_files = {}

    for category in ("accessibility", "seo", "ux"):
        path = tmp_path / f"{category}.json"

        path.write_text(
            f"""
            {{
                "category": "{category}",
                "summary": "Test summary",
                "findings": [
                    {{
                        "title": "Test issue",
                        "severity": "medium",
                        "description": "Test description",
                        "recommendation": "Test recommendation",
                        "evidence": ["Test evidence"]
                    }}
                ]
            }}
            """,
            encoding="utf-8"
        )

        analysis_files[category] = str(path)

    result = analyse_page({
        "analysis_files": analysis_files
    })

    assert len(result["findings"]) == 6
    assert any(
        "Test recommendation" in finding
        for finding in result["findings"]
    )