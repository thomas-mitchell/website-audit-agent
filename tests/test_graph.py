import json
from pathlib import Path

from auditor.graph import build_graph


def test_audit_graph(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <html>
        <head><title>Example University</title></head>
        <body>
            <h1>Welcome</h1>
            <p>Explore our courses.</p>
        </body>
    </html>
    """

    test_file = tmp_path / "test.html"
    test_file.write_text(html, encoding="utf-8")

    def mock_lighthouse(state):
        path = tmp_path / "lighthouse.json"
        path.write_text(
            json.dumps({
                "categories": {
                    "performance": {"score": 0.95}
                }
            }),
            encoding="utf-8"
        )
        return {"evidence_files": {"lighthouse": str(path)}}

    def mock_axe(state):
        path = tmp_path / "axe.json"
        path.write_text(
            json.dumps({"violations": []}),
            encoding="utf-8"
        )
        return {"evidence_files": {"axe": str(path)}}

    graph = build_graph(
        lighthouse_node=mock_lighthouse,
        axe_node=mock_axe
    )

    result = graph.invoke({
        "url": test_file.as_uri(),
        "run_id": "graph-test",
        "evidence_files": {},
        "findings": [],
        "report": ""
    })

    assert "Example University" in result["report"]
    assert "Lighthouse performance: 95/100" in result["report"]
    assert "axe-core: 0 accessibility" in result["report"]

    assert Path(result["evidence_files"]["page"]).exists()
    assert Path(result["evidence_files"]["lighthouse"]).exists()
    assert Path(result["evidence_files"]["axe"]).exists()