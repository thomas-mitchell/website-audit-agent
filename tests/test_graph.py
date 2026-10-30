import json
from pathlib import Path
import asyncio

from auditor.graph import build_graph
from auditor.models.findings import Finding
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationResult,
    InvestigationType,
)

def test_audit_graph(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Create a local test webpage
    html = """
    <html>
        <head>
            <title>Example University</title>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>Explore our courses.</p>
        </body>
    </html>
    """

    test_file = tmp_path / "test.html"
    test_file.write_text(html, encoding="utf-8")

    # Mock Lighthouse
    def mock_lighthouse(state):
        path = tmp_path / "lighthouse.json"

        path.write_text(
            json.dumps({
                "categories": {
                    "performance": {"score": 0.95},
                    "accessibility": {"score": 0.90},
                    "seo": {"score": 1.0}
                },
                "audits": {}
            }),
            encoding="utf-8"
        )

        return {
            "evidence_files": {
                "lighthouse": str(path)
            }
        }

    # Mock axe-core
    def mock_axe(state):
        path = tmp_path / "axe.json"

        path.write_text(
            json.dumps({
                "violations": [
                    {
                        "id": "image-alt",
                        "impact": "serious",
                        "description": "Images must have alt text",
                        "help": "Images must have alternative text",
                        "nodes": []
                    }
                ]
            }),
            encoding="utf-8"
        )

        return {
            "evidence_files": {
                "axe": str(path)
            }
        }

    # Factory for creating mock AI analysts
    def mock_analyst(category):
        def analyse(state):
            output_dir = (
                Path("runs")
                / state["run_id"]
                / "analysis"
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            path = output_dir / f"{category}.json"

            path.write_text(
                json.dumps({
                    "category": category,
                    "summary": f"Test {category} summary",
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

            return {
                "analysis_files": {
                    category: str(path)
                }
            }

        return analyse

    review_calls = 0
    def mock_review(state):
        nonlocal review_calls

        review_calls += 1

        if review_calls == 1:
            return {
                "findings": state["findings"],
                "investigations": [
                    InvestigationRequest(
                        finding_title="Test accessibility issue",
                        investigation_type=InvestigationType.ACCESSIBILITY,
                        question="Is the footer exposed as a landmark?",
                        target="footer",
                    )
                ],
            }

        return {
            "findings": state["findings"],
            "investigations": [],
        }

    async def mock_investigate(state):
        return {
            "investigation_results": [
                InvestigationResult(
                    finding_title="Test accessibility issue",
                    question="Is the footer exposed as a landmark?",
                    answer="The footer is exposed as contentinfo.",
                    evidence=["Accessibility snapshot: contentinfo"],
                    resolved=True,
                )
            ]
        }

    # Build graph with mocked external tools and LLMs
    graph = build_graph(
        lighthouse_node=mock_lighthouse,
        axe_node=mock_axe,
        accessibility_node=mock_analyst("accessibility"),
        seo_node=mock_analyst("seo"),
        ux_node=mock_analyst("ux"),
        review_node=mock_review,
        investigation_node=mock_investigate
    )

    # Execute the complete graph
    async def run_graph():
        return await graph.ainvoke({
            "url": test_file.as_uri(),
            "run_id": "graph-test",
            "evidence_files": {},
            "prepared_evidence": "",
            "analysis_files": {},
            "findings": [],
            "investigations": [],
            "investigation_results": [],
            "report": ""
        })

    result = asyncio.run(run_graph())

    # Verify page capture
    assert Path(
        result["evidence_files"]["page"]
    ).exists()

    # Verify automated audit evidence
    assert Path(
        result["evidence_files"]["lighthouse"]
    ).exists()

    assert Path(
        result["evidence_files"]["axe"]
    ).exists()

    # Verify prepared evidence
    prepared_path = Path(result["prepared_evidence"])
    assert prepared_path.exists()

    prepared = json.loads(
        prepared_path.read_text(encoding="utf-8")
    )

    assert prepared["title"] == "Example University"
    assert prepared["lighthouse"]["scores"]["performance"] == 0.95
    assert len(prepared["axe"]["violations"]) == 1

    # Verify all three AI analysts executed
    assert set(result["analysis_files"]) == {
        "accessibility",
        "seo",
        "ux"
    }

    for path in result["analysis_files"].values():
        assert Path(path).exists()

    # Verify aggregation
    assert len(result["findings"]) == 3
    assert all(isinstance(f, Finding) for f in result["findings"])

    assert {f.title for f in result["findings"]} == {
        "Test accessibility issue",
        "Test seo issue",
        "Test ux issue",
    }

    # Verify final report
    assert "Example University" in result["report"]
    assert "Test accessibility issue" in result["report"]
    assert "Test seo issue" in result["report"]
    assert "Test ux issue" in result["report"]
    assert review_calls == 2
    assert len(result["investigation_results"]) == 1
    assert result["investigation_results"][0].resolved is True
    assert result["investigations"] == []