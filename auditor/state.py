from typing import Annotated, TypedDict


def merge_dicts(
    existing: dict[str, str],
    update: dict[str, str]
) -> dict[str, str]:
    return {**existing, **update}

class AuditState(TypedDict):
    url: str
    run_id: str

    # References to captured evidence
    evidence_files: Annotated[
        dict[str, str],
        merge_dicts
    ]

    # Analysis results
    findings: list[str]

    # Final report
    report: str