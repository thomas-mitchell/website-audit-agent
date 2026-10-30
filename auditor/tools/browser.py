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