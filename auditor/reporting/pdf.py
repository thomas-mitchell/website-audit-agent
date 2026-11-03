from pathlib import Path
from html import escape

import markdown
import bleach
from playwright.async_api import async_playwright


CSS_PATH = Path(__file__).with_name("report.css")


async def generate_pdf(
    markdown_path: Path,
    output_path: Path,
) -> Path:
    """Convert a Markdown audit report into a styled PDF."""

    markdown_path = markdown_path.resolve()
    output_path = output_path.resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown_text = markdown_path.read_text(encoding="utf-8")

    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code"],
    )

    body = bleach.clean(
        body,
        tags=[
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "strong", "em", "ul", "ol", "li",
            "table", "thead", "tbody", "tr", "th", "td",
            "blockquote", "pre", "code", "br", "hr",
            "a", "img",
        ],
        attributes={
            "a": ["href", "title"],
            "img": ["src", "alt", "title"],
            "th": ["align"],
            "td": ["align"],
        },
        protocols=["http", "https", "mailto"],
        strip=True,
    )

    css = CSS_PATH.read_text(encoding="utf-8")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Website Quality Audit</title>
    <style>{css}</style>
</head>
<body>
    <main class="report">
        {body}
    </main>
</body>
</html>
"""

    # Save the HTML as an intermediate artifact.
    # Loading it from disk lets Chromium resolve relative screenshot paths.
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            await page.goto(
                html_path.as_uri(),
                wait_until="load",
            )

            await page.evaluate("""
                async () => {
                    await document.fonts.ready;

                    await Promise.all(
                        Array.from(document.images).map(img => {
                            if (img.complete) return Promise.resolve();

                            return new Promise(resolve => {
                                img.addEventListener("load", resolve, {
                                    once: true
                                });
                                img.addEventListener("error", resolve, {
                                    once: true
                                });
                            });
                        })
                    );
                }
            """)

            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template="""
                    <div style="
                        font-size: 9px;
                        color: #64748b;
                        width: 100%;
                        text-align: right;
                        padding-right: 18mm;
                    ">
                        Page <span class="pageNumber"></span>
                        of <span class="totalPages"></span>
                    </div>
                """,
                margin={
                    "top": "18mm",
                    "bottom": "22mm",
                    "left": "18mm",
                    "right": "18mm",
                },
            )

        finally:
            await browser.close()

    print(f"PDF report saved: {output_path}")

    return output_path