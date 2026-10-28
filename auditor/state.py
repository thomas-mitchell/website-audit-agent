from typing import TypedDict


class AuditState(TypedDict):
    url: str
    run_id: str

    # References to captured evidence
    evidence_files: dict[str, str]

    # Analysis results
    findings: list[str]

    # Final report
    report: str