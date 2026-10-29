import json
from pathlib import Path

from auditor.state import AuditState


def load_json(path: str) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def prepare_evidence(state: AuditState) -> dict:
    print("Preparing evidence for AI analysis...")

    files = state["evidence_files"]

    page = load_json(files["page"])
    lighthouse = load_json(files["lighthouse"])
    axe = load_json(files["axe"])

    # Extract Lighthouse category scores
    lighthouse_scores = {
        name: data.get("score")
        for name, data in lighthouse.get(
            "categories", {}
        ).items()
    }

    # Extract individual Lighthouse audit details.
    # Only retain failed or advisory audits.
    lighthouse_issues = []

    for audit_id, audit in lighthouse.get(
        "audits", {}
    ).items():
        score = audit.get("score")
        score_mode = audit.get("scoreDisplayMode")

        if (
            score is not None
            and score < 1
            and score_mode not in (
                "notApplicable",
                "manual",
                "informative"
            )
        ):
            lighthouse_issues.append({
                "id": audit_id,
                "title": audit.get("title"),
                "description": audit.get("description"),
                "score": score
            })

    # Extract axe-core violations
    axe_violations = []

    for violation in axe.get("violations", []):
        axe_violations.append({
            "id": violation.get("id"),
            "impact": violation.get("impact"),
            "description": violation.get("description"),
            "help": violation.get("help"),
            "help_url": violation.get("helpUrl"),
            "nodes": [
                {
                    "html": node.get("html"),
                    "target": node.get("target"),
                    "failure_summary": node.get(
                        "failureSummary"
                    )
                }
                for node in violation.get("nodes", [])
            ]
        })

    prepared = {
        "url": page.get("url"),
        "title": page.get("title"),
        "description": page.get("description"),
        "canonical": page.get("canonical"),
        "robots": page.get("robots"),
        "status_code": page.get("status_code"),
        "headings": page.get("headings", []),
        "links": page.get("links", [])[:100],   # TODO Revisit limits
        "images": page.get("images", [])[:100],
        "text": page.get("text", "")[:15000],
        "lighthouse": {
            "scores": lighthouse_scores,
            "issues": lighthouse_issues
        },
        "axe": {
            "violations": axe_violations
        }
    }

    output_dir = (
        Path("runs")
        / state["run_id"]
        / "evidence"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = output_dir / "prepared.json"

    output_path.write_text(
        json.dumps(prepared, indent=2),
        encoding="utf-8"
    )

    return {
        "prepared_evidence": str(output_path)
    }