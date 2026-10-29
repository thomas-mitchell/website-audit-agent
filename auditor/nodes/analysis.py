from auditor.models.findings import AnalysisResult, Finding
from auditor.state import AuditState


def analyse_page(state: AuditState) -> dict:
    findings: list[Finding] = []

    for category, file_path in state["analysis_files"].items():
        with open(file_path, encoding="utf-8") as f:
            analysis = AnalysisResult.model_validate_json(f.read())

        findings.extend(analysis.findings)

    return {"findings": findings}