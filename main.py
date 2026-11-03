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

    report_dir = (
        Path("runs")
        / result["run_id"]
        / "reports"
    )

    print()
    print(f"Markdown: {(report_dir / 'audit.md').resolve()}")
    print(f"HTML:     {(report_dir / 'audit.html').resolve()}")
    print(f"PDF:      {(report_dir / 'audit.pdf').resolve()}")

    print()
    print("Analysis files:")

    for category, path in result["analysis_files"].items():
        print(f"  {category}: {path}")


if __name__ == "__main__":
    asyncio.run(main())