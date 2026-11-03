import json
import os
import re
from html import escape
from collections import Counter
from pathlib import Path
import re
from html import escape

from auditor.models.findings import Severity
from auditor.state import AuditState
from auditor.reporting.pdf import generate_pdf


SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]

HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")


def escape_html_in_markdown(text: str) -> str:
    """Preserve HTML snippets as visible text in Markdown."""
    return HTML_TAG.sub(
        lambda match: escape(match.group(0)),
        text,
    )

def format_analysis_answer(answer: str) -> list[str]:
    """Keep generated analysis visually subordinate to its finding."""
    return [
        f"> {escape_html_in_markdown(line)}" if line.strip() else ">"
        for line in answer.splitlines()
    ]

def format_screenshot_evidence(investigation, report_dir: Path) -> list[str]:
    """Format investigation screenshots as Markdown."""

    lines = []

    for screenshot in investigation.screenshots:
        screenshot_path = Path(screenshot.path).resolve()

        # Markdown image paths must be relative to the report directory.
        relative_path = Path(
            os.path.relpath(screenshot_path, report_dir.resolve())
        ).as_posix()

        lines.extend([
            "",
            f"**Screenshot type:** {screenshot.capture_type}",
            "",
            f"![Investigation screenshot]({relative_path})",
            "",
        ])

        if screenshot.selector:
            lines.append(
                f"**Element selector:** `{screenshot.selector}`"
            )
            lines.append("")

        lines.append(
            f"**Visually analysed:** "
            f"{'Yes' if screenshot.analysed else 'No'}"
        )

        if screenshot.analysed and screenshot.analysis_answer:
            lines.extend([
                "",
                "**Visual observations:**",
                "",
                escape_html_in_markdown(screenshot.analysis_answer),
            ])

    return lines


def render_markdown_report(
    state: AuditState,
    page_data: dict,
    report_dir: Path,
) -> str:
    """Render a Markdown report from structured audit results."""

    findings = state["findings"]

    severity_counts = Counter(
        finding.severity for finding in findings
    )

    investigations_by_finding = {}

    for investigation in state.get("investigation_results", []):
        investigations_by_finding.setdefault(
            investigation.finding_id,
            [],
        ).append(investigation)

    lines = [
        "# Website Quality Audit",
        "",
        f"**Website:** {page_data['title']}",
        "",
        f"**URL:** {state['url']}",
        "",
        f"**HTTP Status:** {page_data['status_code']}",
        "",
        "## Executive Summary",
        "",
        f"**Total findings:** {len(findings)}",
        "",
        "| Severity | Findings |",
        "| --- | ---: |",
    ]

    for severity in SEVERITY_ORDER:
        lines.append(
            f"| {severity.value.title()} | "
            f"{severity_counts[severity]} |"
        )

    lines.extend([
        "",
        "## Findings",
    ])

    if not findings:
        lines.extend([
            "",
            "No findings were reported by the audit.",
        ])

    for index, finding in enumerate(findings, start=1):
        lines.extend([
            "",
            f"### {index}. {finding.title}",
            "",
            f"**Finding ID:** `{finding.id}`",
            "",
            f"**Severity:** {finding.severity.value.upper()}",
            "",
            f"**Status:** {finding.status.value.upper()}",
            "",
            "#### Description",
            "",
            escape_html_in_markdown(finding.description),
            "",
            "#### Impact",
            "",
            escape_html_in_markdown(finding.impact),
            "",
            "#### Recommendation",
            "",
            escape_html_in_markdown(finding.recommendation),
        ])

        if finding.evidence:
            lines.extend([
                "",
                "#### Supporting Evidence",
                "",
            ])

            for evidence in finding.evidence:
                lines.append(f"- {escape_html_in_markdown(evidence)}")

        if finding.reproduction_steps:
            lines.extend([
                "",
                "#### Reproduction Steps",
                "",
            ])

            for step_index, step in enumerate(
                finding.reproduction_steps, start=1
            ):
                lines.append(f"{step_index}. {escape_html_in_markdown(step)}")

        if finding.references:
            lines.extend([
                "",
                "#### References",
                "",
            ])

            for reference in finding.references:
                lines.append(f"- {reference}")

        for investigation in investigations_by_finding.get(
            finding.id, []
        ):
            lines.extend([
                "",
                "#### Investigation",
                "",
                f"**Question:** {escape_html_in_markdown(investigation.question)}",
                "",
                f"**Result:** {escape_html_in_markdown(investigation.answer)}",
                "",
                f"**Resolved:** "
                f"{'Yes' if investigation.resolved else 'No'}",
            ])

            if investigation.screenshots:
                lines.extend([
                    "",
                    "##### Visual Evidence",
                ])

                lines.extend(
                    format_screenshot_evidence(
                        investigation,
                        report_dir,
                    )
                )

    # Preserve evidence from investigations whose findings were
    # removed or whose IDs changed during the final review.
    finding_ids = {
        finding.id for finding in findings
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
            "## Additional Investigation Evidence",
        ])

        for investigation in unmatched:
            lines.extend([
                "",
                f"### {escape_html_in_markdown(investigation.finding_title)}",
                "",
                escape_html_in_markdown(investigation.answer),
            ])

            lines.extend(
                format_screenshot_evidence(
                    investigation,
                    report_dir,
                )
            )

    return "\n".join(lines).rstrip() + "\n"


async def generate_report(state: AuditState) -> dict:
    """Generate and save the Markdown audit report."""

    print("Generating Markdown report...")

    page_path = Path(state["evidence_files"]["page"])

    page_data = json.loads(
        page_path.read_text(encoding="utf-8")
    )

    report_dir = Path("runs") / state["run_id"] / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    markdown = render_markdown_report(
        state,
        page_data,
        report_dir,
    )

    report_path = report_dir / "audit.md"

    report_path.write_text(
        markdown,
        encoding="utf-8",
    )

    print(f"Markdown report saved: {report_path}")

    pdf_path = report_dir / "audit.pdf"

    await generate_pdf(
        markdown_path=report_path,
        output_path=pdf_path,
    )

    return {
        "report": markdown,
    }