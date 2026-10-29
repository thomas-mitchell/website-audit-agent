from playwright.sync_api import sync_playwright

from auditor.tools.browser import inspect_element
from auditor.tools.session import BrowserSession
from auditor.tools.langchain_browser import create_browser_tools

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

def test_browser_session_and_langchain_tool(tmp_path):
    html = """
    <html>
        <body>
            <main>
                <h1>Test Page</h1>
                <footer>Footer content</footer>
            </main>
        </body>
    </html>
    """

    test_file = tmp_path / "test.html"
    test_file.write_text(html, encoding="utf-8")

    with BrowserSession(test_file.as_uri()) as session:
        tools = create_browser_tools(session)

        assert len(tools) == 1
        assert tools[0].name == "inspect_element"

        result = tools[0].invoke({
            "selector": "footer"
        })

        assert result["match_count"] == 1
        assert result["elements"][0]["tag"] == "footer"
        assert result["elements"][0]["visible"] is True