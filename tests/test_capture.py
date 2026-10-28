import json
from pathlib import Path

from auditor.nodes.capture import capture_page


def test_capture_page(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <html>
        <head>
            <title>Test Website</title>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>This is a test page.</p>
            <a href="/about">About Us</a>
        </body>
    </html>
    """

    # We'll use a local HTML file rather than a remote URL.
    test_file = tmp_path / "test.html"
    test_file.write_text(html, encoding="utf-8")

    result = capture_page({
        "url": test_file.as_uri(),
        "run_id": "test-run",
        "evidence_files": {},
        "findings": [],
        "report": ""
    })

    page_path = Path(result["evidence_files"]["page"])

    assert page_path.exists()

    page_data = json.loads(
        page_path.read_text(encoding="utf-8")
    )

    assert page_data["title"] == "Test Website"
    assert "Welcome" in page_data["headings"]
    assert "This is a test page" in page_data["text"]

    assert Path(
        result["evidence_files"]["html"]
    ).exists()

    assert Path(
        result["evidence_files"]["screenshot"]
    ).exists()