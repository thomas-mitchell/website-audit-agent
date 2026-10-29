from playwright.sync_api import sync_playwright

from auditor.tools.browser import inspect_element


def test_inspect_element(tmp_path):
    html = """
    <html>
        <body>
            <main>
                <h1>Hello World</h1>
                <footer style="display: none">
                    Hidden footer
                </footer>
            </main>
        </body>
    </html>
    """

    test_file = tmp_path / "test.html"
    test_file.write_text(html, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()
            page.goto(test_file.as_uri())

            result = inspect_element(page, "footer")

            assert result["match_count"] == 1
            assert result["elements"][0]["tag"] == "footer"
            assert result["elements"][0]["display"] == "none"
            assert result["elements"][0]["visible"] is False

        finally:
            browser.close()