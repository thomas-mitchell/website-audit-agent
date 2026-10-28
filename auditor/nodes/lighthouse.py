import os
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from auditor.state import AuditState


def run_lighthouse(state: AuditState) -> dict:
    url = state["url"]
    run_id = state["run_id"]

    print(f"Running Lighthouse: {url}")

    output_dir = Path("runs") / run_id / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "lighthouse.json"

    # Use the Chromium installation managed by Playwright.
    with sync_playwright() as playwright:
        chrome_path = playwright.chromium.executable_path

    env = os.environ.copy()
    env["CHROME_PATH"] = chrome_path

    # On Windows, npm exposes npx as npx.cmd.
    npx = "npx.cmd" if sys.platform == "win32" else "npx"

    command = [
        npx,
        "--no-install",
        "lighthouse",
        url,
        "--output=json",
        f"--output-path={output_path.resolve()}",
        "--chrome-flags=--headless",
        "--quiet",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Lighthouse failed:\n{result.stderr}"
        )

    if not output_path.exists():
        raise RuntimeError(
            "Lighthouse completed but produced no report."
        )

    return {
        "evidence_files": {
            "lighthouse": str(output_path)
        }
    }