import asyncio

from auditor.agents.investigator import investigate
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationType,
)


request = InvestigationRequest(
    finding_title="Potential broken anchor navigation",
    investigation_type=InvestigationType.ANCHOR,
    question=(
        "Does clicking the link targeting #talent-fake navigate "
        "to the intended section of the page? "
        "Check whether the URL fragment changes, whether the page "
        "scrolls, and whether the destination element exists."
    ),
    target="#talent-fake",
)

result = asyncio.run(
    investigate(
        url="https://www.boomworks.com.au/",
        request=request,
    )
)

print(result.model_dump_json(indent=2))