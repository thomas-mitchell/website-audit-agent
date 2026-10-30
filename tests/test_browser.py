import asyncio

from playwright.async_api import async_playwright

from auditor.tools.browser import inspect_element
from auditor.tools.session import BrowserSession
from auditor.tools.langchain_browser import create_browser_tools


def test_inspect_element(tmp_path):
    async def run_test():
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

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)

            try:
                page = await browser.new_page()
                await page.goto(test_file.as_uri())

                result = await inspect_element(page, "footer")

                assert result["match_count"] == 1
                assert result["elements"][0]["tag"] == "footer"
                assert result["elements"][0]["display"] == "none"
                assert result["elements"][0]["visible"] is False

            finally:
                await browser.close()

    asyncio.run(run_test())


def test_browser_session_and_langchain_tool(tmp_path):
    async def run_test():
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

        async with BrowserSession(test_file.as_uri()) as session:
            tools = create_browser_tools(session)

            assert len(tools) == 2
            assert tools[0].name == "inspect_element"
            assert tools[1].name == "inspect_accessibility"

            result = await tools[0].ainvoke({
                "selector": "footer"
            })

            assert result["match_count"] == 1
            assert result["elements"][0]["tag"] == "footer"
            assert result["elements"][0]["visible"] is True

    asyncio.run(run_test())


def test_inspect_accessibility(tmp_path):
    async def run_test():
        html = """
        <html>
            <body>
                <header>
                    <nav aria-label="Primary">
                        <a href="/about">About Us</a>
                    </nav>
                </header>

                <main>
                    <h1>Welcome</h1>
                </main>

                <footer aria-label="Contact information">
                    <a href="/contact">Contact Us</a>
                </footer>
            </body>
        </html>
        """

        test_file = tmp_path / "test.html"
        test_file.write_text(html, encoding="utf-8")

        async with BrowserSession(test_file.as_uri()) as session:
            tools = create_browser_tools(session)

            accessibility_tool = next(
                tool for tool in tools
                if tool.name == "inspect_accessibility"
            )

            result = await accessibility_tool.ainvoke({
                "selector": "body"
            })

            assert result["match_count"] == 1

            snapshot = result["elements"][0]["snapshot"]

            assert 'navigation "Primary"' in snapshot
            assert "main:" in snapshot
            assert 'contentinfo "Contact information"' in snapshot
            assert 'link "Contact Us"' in snapshot

    asyncio.run(run_test())