import json
from pathlib import Path

from auditor.state import AuditState


def load_json(path: str) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def analyse_page(state: AuditState) -> dict:
    print("Analysing audit evidence...")

    evidence = state["evidence_files"]

    page_data = load_json(evidence["page"])
    lighthouse_data = load_json(evidence["lighthouse"])
    axe_data = load_json(evidence["axe"])

    findings = []

    # Existing basic checks
    if not page_data["title"]:
        findings.append("Page has no title.")

    if not page_data["headings"]:
        findings.append("Page has no headings.")

    if not page_data["text"].strip():
        findings.append("Page contains no visible text.")

    # Lighthouse scores
    categories = lighthouse_data.get("categories", {})

    for category, data in categories.items():
        score = data.get("score")

        if score is not None:
            findings.append(
                f"Lighthouse {category}: {score * 100:.0f}/100"
            )

    # axe-core violations
    violations = axe_data.get("violations", [])

    findings.append(
        f"axe-core: {len(violations)} accessibility "
        f"rule violations detected."
    )

    for violation in violations:
        findings.append(
            f"Accessibility [{violation.get('impact')}]: "
            f"{violation.get('help')} "
            f"({len(violation.get('nodes', []))} affected elements)"
        )

    return {
        "findings": findings
    }