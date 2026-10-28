from pathlib import Path

from auditor.graph import build_graph


def test_audit_graph(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

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

    graph = build_graph()

    result = graph.invoke({
        "url": test_file.as_uri(),
        "run_id": "graph-test",
        "evidence_files": {},
        "findings": [],
        "report": ""
    })

    assert "Example University" in result["report"]
    assert "No issues detected" in result["report"]

    assert Path(
        result["evidence_files"]["page"]
    ).exists()