import json
from pathlib import Path

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

from auditor.state import AuditState


def run_axe(state: AuditState) -> dict:
    url = state["url"]
    run_id = state["run_id"]

    print(f"Running axe-core: {url}")

    output_dir = Path("runs") / run_id / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "axe.json"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 900}
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(1000)

            axe = Axe()
            results = axe.run(page)

            output_path.write_text(
                json.dumps(
                    results.response,
                    indent=2
                ),
                encoding="utf-8"
            )

            print(
                f"axe-core found "
                f"{results.violations_count} violations."
            )

        finally:
            browser.close()

    return {
        "evidence_files": {
            "axe": str(output_path)
        }
    }