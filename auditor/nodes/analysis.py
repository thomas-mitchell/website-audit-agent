import json
from pathlib import Path

from auditor.state import AuditState


def analyse_page(state: AuditState) -> dict:
    print("Analysing page...")

    page_path = Path(state["evidence_files"]["page"])

    page_data = json.loads(
        page_path.read_text(encoding="utf-8")
    )

    findings = []

    # Simple deterministic checks for now
    if not page_data["title"]:
        findings.append("Page has no title.")

    if not page_data["headings"]:
        findings.append("Page has no headings.")

    if not page_data["text"].strip():
        findings.append("Page contains no visible text.")

    return {
        "findings": findings
    }