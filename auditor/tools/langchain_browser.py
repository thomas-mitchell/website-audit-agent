from langchain_core.tools import tool
from playwright.async_api import Error as PlaywrightError

from auditor.tools.session import BrowserSession


def selector_error(selector: str, exc: PlaywrightError) -> dict:
    """Convert a Playwright selector error into actionable feedback."""

    return {
        "selector": selector,
        "success": False,
        "error": str(exc).splitlines()[0],
        "hint": (
            "Check the selector syntax and retry. "
            "Use Playwright-supported selectors. "
            "For text matching, use :has-text(), not :contains(). "
            'Example: p:has-text("Our Partners"). '
            "You can also use text=Our Partners."
        ),
    }

def create_browser_tools(session: BrowserSession):

    @tool
    async def inspect_element(selector: str) -> dict:
        """Inspect DOM elements matching a Playwright selector.

        Supports CSS selectors and Playwright text selectors.

        Examples:
        - footer
        - #talent-fake
        - a[href="#talent-fake"]
        - p:has-text("Our Partners")
        - text=Years of Experience

        Do not use jQuery :contains() syntax.
        """
        try:
            return await session.inspect_element(selector)
        except PlaywrightError as exc:
            return selector_error(selector, exc)

    @tool
    async def inspect_accessibility(
        selector: str = "body",
    ) -> dict:
        """Inspect the browser's accessible structure.

        Returns accessibility snapshots containing semantic roles,
        accessible names and descendant elements.

        Accepts Playwright selectors, including :has-text().
        Do not use jQuery :contains() syntax.

        This does not constitute real screen-reader testing.
        """
        try:
            return await session.inspect_accessibility(selector)
        except PlaywrightError as exc:
            return selector_error(selector, exc)

    @tool
    async def inspect_scroll_position() -> dict:
        """Inspect the browser's current scroll position.

        Returns the current URL, fragment identifier, scroll coordinates,
        viewport dimensions and document dimensions.

        Use this to investigate anchor navigation and scrolling behaviour.
        """
        return await session.inspect_scroll_position()


    @tool
    async def click_element(selector: str) -> dict:
        """Click a single element matching a Playwright selector.

        Returns browser state before and after the click, including URL
        changes, fragment changes and scrolling changes.

        Do not use jQuery :contains() syntax.

        Only click safe, non-destructive controls.
        """
        try:
            return await session.click_element(selector)
        except PlaywrightError as exc:
            return selector_error(selector, exc)

    
    return [
        inspect_element,
        inspect_accessibility,
        inspect_scroll_position,
        click_element,
    ]
