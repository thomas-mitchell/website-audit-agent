import asyncio
from pathlib import Path

from auditor.agents.investigator import investigate
from auditor.models.investigation import InvestigationResult
from auditor.state import AuditState


async def investigate_findings(state: AuditState) -> dict:
    """Investigate the questions raised by the reviewer."""

    requests = state.get("investigations", [])

    print(f"Investigating {len(requests)} findings...")

    results: list[InvestigationResult] = []

    for index, request in enumerate(requests, start=1):
        print(
            f"Investigation {index}/{len(requests)}: "
            f"{request.finding_title}"
        )

        try:
            result = await investigate(
                url=state["url"],
                request=request,
            )

        except Exception as exc:
            print(f"Investigation failed: {exc}")

            result = InvestigationResult(
                finding_title=request.finding_title,
                question=request.question,
                answer=(
                    "The investigation could not be completed "
                    f"because an error occurred: {exc}"
                ),
                evidence=[],
                resolved=False,
            )

        results.append(result)

    output_dir = (
        Path("runs")
        / state["run_id"]
        / "analysis"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "investigations.json"

    output_path.write_text(
        "[\n"
        + ",\n".join(
            result.model_dump_json(indent=2)
            for result in results
        )
        + "\n]",
        encoding="utf-8",
    )

    return {
        "investigation_results": results,
    }