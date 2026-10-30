from playwright.async_api import async_playwright

from auditor.tools.browser import (
    inspect_element,
    inspect_accessibility,
    inspect_scroll_position,
    click_element,
)


class BrowserSession:
    def __init__(self, url: str):
        self.url = url
        self.playwright = None
        self.browser = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        try:
            self.browser = await self.playwright.chromium.launch(
                headless=True
            )

            self.page = await self.browser.new_page(
                viewport={"width": 1440, "height": 900}
            )

            await self.page.goto(
                self.url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            await self.page.wait_for_timeout(1000)

            return self

        except Exception:
            await self.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

    async def inspect_element(self, selector: str) -> dict:
        return await inspect_element(self.page, selector)

    async def inspect_accessibility(
        self,
        selector: str = "body",
    ) -> dict:
        return await inspect_accessibility(self.page, selector)

    async def inspect_scroll_position(self) -> dict:
        return await inspect_scroll_position(self.page)

    async def click_element(self, selector: str) -> dict:
        return await click_element(self.page, selector)