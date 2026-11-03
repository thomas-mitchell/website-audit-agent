import asyncio
import json
from pathlib import Path

from auditor.agents.investigator import investigate
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationType,
)


async def main():
    request = InvestigationRequest(
        finding_title="Partner images may lack meaningful alternative text",
        investigation_type=InvestigationType.VISUAL,
        question=(
            "Does the 'Our Partners' section contain visible partner "
            "logos or organisation names that communicate information? "
            "Use screenshot analysis to establish what is visible. "
            "Inspect the DOM attributes of one or two representative "
            "logo images if possible. You do not need to examine "
            "every image. Clearly distinguish visual observations "
            "from conclusions about alternative text."
        ),
        target="Our Partners section",
    )

    result = await investigate(
        url="https://www.boomworks.com.au/",
        request=request,
        output_dir=(
            Path("runs")
            / "visual-investigator-test"
            / "evidence"
            / "screenshots"
        ),
    )

    print(json.dumps(
        result.model_dump(mode="json"),
        indent=2,
    ))


if __name__ == "__main__":
    asyncio.run(main())