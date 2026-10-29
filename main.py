from uuid import uuid4

from auditor.graph import build_graph


def main():
    graph = build_graph()

    result = graph.invoke({
        "url": "https://example.com",
        "run_id": str(uuid4()),
        "evidence_files": {},
        "prepared_evidence": "",
        "analysis_files": {},
        "findings": [],
        "report": ""
    })

    print()
    print(result["report"])

    print()
    print("Analysis files:")

    for category, path in result["analysis_files"].items():
        print(f"  {category}: {path}")


if __name__ == "__main__":
    main()