from playwright.sync_api import sync_playwright

from auditor.tools.browser import inspect_element


class BrowserSession:
    def __init__(self, url: str):
        self.url = url
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.launch(
                headless=True
            )

            self.page = self.browser.new_page(
                viewport={"width": 1440, "height": 900}
            )

            self.page.goto(
                self.url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            self.page.wait_for_timeout(1000)

            return self

        except Exception:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

    def inspect_element(self, selector: str) -> dict:
        return inspect_element(self.page, selector)