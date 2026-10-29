from auditor.models.findings import AnalysisResult
from auditor.state import AuditState


def analyse_page(state: AuditState) -> dict:
    print("Aggregating AI findings...")

    findings = []

    for category in (
        "accessibility",
        "seo",
        "ux"
    ):
        path = state["analysis_files"][category]

        result = AnalysisResult.model_validate_json(
            open_file(path)
        )

        findings.append(
            f"{category.upper()}: {result.summary}"
        )

        for finding in result.findings:
            findings.append(
                f"[{finding.severity.value.upper()}] "
                f"{finding.title}\n"
                f"  {finding.description}\n"
                f"  Recommendation: "
                f"{finding.recommendation}"
            )

    return {
        "findings": findings
    }


def open_file(path: str) -> str:
    from pathlib import Path

    return Path(path).read_text(
        encoding="utf-8"
    )