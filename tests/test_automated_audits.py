import json
from pathlib import Path
from unittest.mock import patch

from auditor.nodes.lighthouse import run_lighthouse
from auditor.nodes.accessibility import run_axe


def test_lighthouse_node(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    state = {
        "url": "https://example.com",
        "run_id": "test-lighthouse",
    }

    def fake_subprocess_run(command, **kwargs):
        output_arg = next(
            arg for arg in command
            if arg.startswith("--output-path=")
        )

        output_path = Path(output_arg.split("=", 1)[1])

        output_path.write_text(
            json.dumps({
                "categories": {
                    "performance": {"score": 0.95}
                }
            }),
            encoding="utf-8"
        )

        return type("Result", (), {
            "returncode": 0,
            "stderr": ""
        })()

    with patch(
        "auditor.nodes.lighthouse.subprocess.run",
        side_effect=fake_subprocess_run
    ):
        result = run_lighthouse(state)

    assert Path(
        result["evidence_files"]["lighthouse"]
    ).exists()


def test_axe_node(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    state = {
        "url": "https://example.com",
        "run_id": "test-axe",
    }

    mock_response = {
        "violations": [
            {
                "id": "image-alt",
                "impact": "critical",
                "help": "Images must have alternative text",
                "nodes": [{"html": "<img src='test.jpg'>"}]
            }
        ]
    }

    with patch(
        "auditor.nodes.accessibility.Axe"
    ) as mock_axe:

        mock_results = mock_axe.return_value.run.return_value
        mock_results.response = mock_response
        mock_results.violations_count = 1

        with patch(
            "auditor.nodes.accessibility.sync_playwright"
        ) as mock_playwright:

            browser = (
                mock_playwright.return_value
                .__enter__.return_value
                .chromium.launch.return_value
            )

            result = run_axe(state)

    output_path = Path(result["evidence_files"]["axe"])

    assert output_path.exists()

    data = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert len(data["violations"]) == 1
    assert data["violations"][0]["id"] == "image-alt"