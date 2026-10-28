from uuid import uuid4

from auditor.graph import build_graph


def main():
    graph = build_graph()

    result = graph.invoke({
        "url": "https://example.com",
        "run_id": str(uuid4()),
        "evidence_files": {},
        "findings": [],
        "report": ""
    })

    print()
    print(result["report"])

    print()
    print("Evidence files:")
    for name, path in result["evidence_files"].items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()