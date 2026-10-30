from langchain_core.tools import tool

from auditor.tools.session import BrowserSession


def create_browser_tools(session: BrowserSession):

    @tool
    async def inspect_element(selector: str) -> dict:
        """Inspect DOM elements matching a CSS selector.

        Returns matching elements, HTML, text, visibility,
        computed styles and bounding boxes.

        Use this to investigate element visibility, attributes,
        duplicate elements and page structure.
        """
        return await session.inspect_element(selector)

    @tool
    async def inspect_accessibility(
        selector: str = "body",
    ) -> dict:
        """Inspect the browser's accessible structure.

        Returns accessibility snapshots containing semantic roles,
        accessible names and descendant elements.

        Use selector='body' to investigate page landmarks such as
        main, navigation, banner and contentinfo.

        This does not constitute real screen-reader testing.
        """
        return await session.inspect_accessibility(selector)

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
        """Click a single element matching a CSS selector.

        Returns browser state before and after the click, including URL
        changes, fragment changes and scrolling changes.

        Use this to investigate navigation links and interactive elements.

        Only click safe, non-destructive controls. Do not submit forms,
        make purchases, delete data or perform other consequential actions.
        """
        return await session.click_element(selector)

    
    return [
        inspect_element,
        inspect_accessibility,
        inspect_scroll_position,
        click_element,
    ]
