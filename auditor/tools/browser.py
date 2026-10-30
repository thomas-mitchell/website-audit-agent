from playwright.async_api import Page


async def inspect_element(page: Page, selector: str) -> dict:
    """Inspect matching DOM elements and their rendered properties."""

    locator = page.locator(selector)
    count = await locator.count()

    elements = []

    for index in range(min(count, 10)):
        element = locator.nth(index)

        details = await element.evaluate("""
            el => {
                const style = getComputedStyle(el);
                const rect = el.getBoundingClientRect();

                return {
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    classes: el.className?.baseVal
                        ?? el.className,
                    text: el.textContent?.trim().slice(0, 300),
                    outer_html: el.outerHTML.slice(0, 1000),
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    aria_hidden: el.getAttribute("aria-hidden"),
                    bounding_box: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    }
                };
            }
        """)

        details["visible"] = await element.is_visible()
        elements.append(details)

    return {
        "selector": selector,
        "match_count": count,
        "elements": elements,
        "truncated": count > 10
    }


async def inspect_accessibility(
    page: Page,
    selector: str = "body",
) -> dict:
    """Inspect the accessible structure of matching elements."""

    locator = page.locator(selector)
    count = await locator.count()

    elements = []

    for index in range(min(count, 10)):
        element = locator.nth(index)

        snapshot = await element.aria_snapshot()

        elements.append({
            "index": index,
            "snapshot": snapshot[:12000],
            "truncated": len(snapshot) > 12000,
        })

    return {
        "selector": selector,
        "match_count": count,
        "elements": elements,
        "truncated": count > 10,
    }

async def inspect_scroll_position(page: Page) -> dict:
    """Return the current browser scroll position and document dimensions."""

    return await page.evaluate("""
        () => ({
            url: window.location.href,
            hash: window.location.hash,
            scroll_x: window.scrollX,
            scroll_y: window.scrollY,
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight,
            document_width: document.documentElement.scrollWidth,
            document_height: document.documentElement.scrollHeight
        })
    """)

from playwright.async_api import TimeoutError as PlaywrightTimeoutError


async def click_element(page: Page, selector: str) -> dict:
    """Click an element and observe the resulting browser state."""

    before = await inspect_scroll_position(page)

    locator = page.locator(selector)
    count = await locator.count()

    if count != 1:
        return {
            "selector": selector,
            "success": False,
            "error": (
                f"Expected exactly one matching element, found {count}"
            ),
            "before": before,
        }

    try:
        await locator.click(timeout=5000)

        # Allow scrolling animations and JavaScript handlers to settle.
        await page.wait_for_timeout(1000)

        after = await inspect_scroll_position(page)

        return {
            "selector": selector,
            "success": True,
            "before": before,
            "after": after,
            "url_changed": before["url"] != after["url"],
            "hash_changed": before["hash"] != after["hash"],
            "scroll_changed": (
                abs(before["scroll_y"] - after["scroll_y"]) > 2
                or abs(before["scroll_x"] - after["scroll_x"]) > 2
            ),
        }

    except PlaywrightTimeoutError as exc:
        return {
            "selector": selector,
            "success": False,
            "error": f"Click timed out: {exc}",
            "before": before,
        }