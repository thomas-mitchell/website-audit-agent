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

    
    return [inspect_element, inspect_accessibility]
