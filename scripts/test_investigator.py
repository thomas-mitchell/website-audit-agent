import asyncio

from auditor.agents.investigator import investigate
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationType,
)


request = InvestigationRequest(
    finding_title="Duplicate footer landmarks",
    investigation_type=InvestigationType.ACCESSIBILITY,
    question=(
        "How many footer elements exist on the page, "
        "and are any hidden using CSS or aria-hidden?"
    ),
    target="footer",
)

result = asyncio.run(
    investigate(
        url="https://www.boomworks.com.au/",
        request=request,
    )
)

print(result.model_dump_json(indent=2))