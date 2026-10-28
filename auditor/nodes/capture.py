import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

from auditor.state import AuditState


def capture_page(state: AuditState) -> dict:
    url = state["url"]
    run_id = state["run_id"]

    print(f"Capturing page: {url}")

    # Create output directory
    output_dir = Path("runs") / run_id / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 900}
            )

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Give client-side rendering a chance to complete.
            # This is a simple starting point, not a universal
            # readiness check for JavaScript-heavy websites.
            page.wait_for_timeout(1000)

            html = page.content()

            page_data = extract_page_data(
                html = html,
                url = page.url,
                status_code = response.status if response else None,
                visible_text = page.locator("body").inner_text()
            )

            # Save HTML
            html_path = output_dir / "page.html"
            html_path.write_text(
                html,
                encoding="utf-8"
            )

            # Save screenshot
            screenshot_path = output_dir / "screenshot.png"
            page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            # Save structured metadata
            json_path = output_dir / "page.json"
            json_path.write_text(
                json.dumps(page_data, indent=2),
                encoding="utf-8"
            )

        finally:
            browser.close()

    return {
        "evidence_files": {
            "html": str(html_path),
            "screenshot": str(screenshot_path),
            "page": str(json_path)
        }
    }


def extract_page_data(
    html: str,
    url: str,
    status_code: int | None,
    visible_text: str
) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Extract base URL from <base> tag if present
    base_element = soup.find("base", href=True)
    base_url = (
        urljoin(url, base_element["href"])
        if base_element
        else url
    )

    # Extract structured page information
    description = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", rel="canonical")
    robots = soup.find("meta", attrs={"name": "robots"})

    return {
        "url": url,
        "title": (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else ""
        ),
        "description": (
            description.get("content") if description else None
        ),
        "canonical": (
            urljoin(base_url, canonical.get("href"))
            if canonical and canonical.get("href")
            else None
        ),
        "robots": (
            robots.get("content") if robots else None
        ),
        "status_code": status_code,
        "headings": [
            {
                "level": int(heading.name[1]),
                "text": heading.get_text(" ", strip=True)
            }
            for heading in soup.select("h1, h2, h3, h4, h5, h6")
        ],
        "links": [
            {
                "text": link.get_text(strip=True),
                "href": urljoin(base_url, link["href"])
            }
            for link in soup.select("a[href]")
        ],
        "text": visible_text,
        "images": [
            {
                "src": urljoin(base_url, img.get("src", "")),
                "alt": img.get("alt"),
                "width": img.get("width"),
                "height": img.get("height")
            }
            for img in soup.select("img")
        ],
    }