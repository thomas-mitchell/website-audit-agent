from pathlib import Path

from auditor.models.findings import AnalysisResult
from auditor.state import AuditState


def analyse_page(state: AuditState) -> dict:
    print("Aggregating AI findings...")

    findings = []

    for category in ("accessibility", "seo", "ux"):
        path = state["analysis_files"][category]

        result = AnalysisResult.model_validate_json(
            Path(path).read_text(encoding="utf-8")
        )

        findings.append(
            f"\n{'=' * 60}\n"
            f"{category.upper()}\n"
            f"{'=' * 60}\n"
            f"{result.summary}"
        )

        for finding in result.findings:
            sections = [
                f"\n{finding.title}",
                f"Severity: {finding.severity.value.upper()}",
                f"Status: {finding.status.value.upper()}",
                f"Description: {finding.description}",
                f"Impact: {finding.impact}",
            ]

            if finding.evidence:
                sections.append(
                    "Evidence:\n" +
                    "\n".join(
                        f"  - {item}"
                        for item in finding.evidence
                    )
                )

            if finding.reproduction_steps:
                sections.append(
                    "Verification steps:\n" +
                    "\n".join(
                        f"  {i}. {step}"
                        for i, step in enumerate(
                            finding.reproduction_steps,
                            start=1
                        )
                    )
                )

            if finding.references:
                sections.append(
                    "References: " +
                    ", ".join(finding.references)
                )

            sections.append(
                f"Recommendation: {finding.recommendation}"
            )

            findings.append("\n".join(sections))

    return {"findings": findings}