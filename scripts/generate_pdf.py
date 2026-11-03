import asyncio
import sys
from pathlib import Path

from auditor.reporting.pdf import generate_pdf


async def main():
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.generate_pdf <audit.md>")
        sys.exit(1)

    markdown_path = Path(sys.argv[1])
    pdf_path = markdown_path.with_suffix(".pdf")

    await generate_pdf(
        markdown_path=markdown_path,
        output_path=pdf_path,
    )


if __name__ == "__main__":
    asyncio.run(main())