import json
from pathlib import Path

from auditor.state import AuditState


def generate_report(state: AuditState) -> dict:
    print("Generating report...")

    page_path = Path(state["evidence_files"]["page"])

    page_data = json.loads(
        page_path.read_text(encoding="utf-8")
    )

    lines = [
        f"Website Audit: {page_data['title']}",
        f"URL: {state['url']}",
        f"HTTP Status: {page_data['status_code']}",
        "",
        "Findings:"
    ]

    if state["findings"]:
        for finding in state["findings"]:
            lines.append(f"- {finding}")
    else:
        lines.append("No issues detected by basic checks.")

    return {
        "report": "\n".join(lines)
    }