import asyncio
from pathlib import Path

from auditor.tools.vision import analyse_screenshot


async def main():
    path = Path("scripts/example-image.png")

    result = await analyse_screenshot(
        path=path,
        question=(
            "Describe the visible contents of this screenshot. "
            "Identify any text, logos or other meaningful information."
        ),
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())