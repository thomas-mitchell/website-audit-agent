import json
from pathlib import Path

from auditor.state import AuditState


def format_screenshot_evidence(investigation) -> list[str]:
    """Format screenshot references for a text report."""

    lines = []

    for screenshot in investigation.screenshots:
        lines.append(f"  Screenshot: {screenshot.path}")
        lines.append(f"    Capture type: {screenshot.capture_type}")

        if screenshot.selector:
            lines.append(f"    Selector: {screenshot.selector}")

        lines.append(
            f"    Visually analysed: {'Yes' if screenshot.analysed else 'No'}"
        )

        if screenshot.analysed and screenshot.analysis_answer:
            lines.append(
                f"    Visual observations: {screenshot.analysis_answer}"
            )

    return lines


def generate_report(state: AuditState) -> dict:
    print("Generating report...")

    page_path = Path(state["evidence_files"]["page"])

    page_data = json.loads(
        page_path.read_text(encoding="utf-8")
    )

    investigations_by_finding = {}

    for investigation in state.get("investigation_results", []):
        investigations_by_finding.setdefault(
            investigation.finding_id,
            [],
        ).append(investigation)

    lines = [
        f"Website Audit: {page_data['title']}",
        f"URL: {state['url']}",
        f"HTTP Status: {page_data['status_code']}",
        "",
        "Findings:"
    ]

    if state["findings"]:
        for finding in state["findings"]:
            lines.extend([
                "",
                finding.title,
                f"Finding ID: {finding.id}",
                f"Severity: {finding.severity.value.upper()}",
                f"Status: {finding.status.value.upper()}",
                f"Description: {finding.description}",
                f"Impact: {finding.impact}",
                f"Recommendation: {finding.recommendation}",
            ])

            for investigation in investigations_by_finding.get(finding.id, []):
                if not investigation.screenshots:
                    continue

                lines.append("")
                lines.append("Visual Evidence:")

                lines.extend(format_screenshot_evidence(investigation))

    else:
        lines.append("No issues detected by basic checks.")

    finding_ids = {
        finding.id
        for finding in state["findings"]
    }

    unmatched = [
        investigation
        for investigation in state.get("investigation_results", [])
        if investigation.finding_id not in finding_ids
        and investigation.screenshots
    ]

    if unmatched:
        lines.extend([
            "",
            "Additional Investigation Evidence:",
        ])

        for investigation in unmatched:
            lines.extend([
                "",
                f"Original finding: {investigation.finding_title}",
            ])

            lines.extend(format_screenshot_evidence(investigation))

    return {
        "report": "\n".join(lines)
    }