import asyncio
from uuid import uuid4
from pathlib import Path

from auditor.graph import build_graph


async def main():
    graph = build_graph()

    result = await graph.ainvoke({
        "url": "https://www.boomworks.com.au/",
        "run_id": str(uuid4()),
        "evidence_files": {},
        "prepared_evidence": "",
        "analysis_files": {},
        "findings": [],
        "investigations": [],
        "investigation_results": [],
        "report": ""
    })

    report_path = (
        Path("runs")
        / result["run_id"]
        / "reports"
        / "audit.md"
    )

    print()
    print(f"Report saved to: {report_path.resolve()}")

    print()
    print("Analysis files:")

    for category, path in result["analysis_files"].items():
        print(f"  {category}: {path}")


if __name__ == "__main__":
    asyncio.run(main())