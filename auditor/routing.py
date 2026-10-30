from typing import Literal

from auditor.state import AuditState


def route_after_review(
    state: AuditState,
) -> Literal["investigate", "report"]:

    # Only one investigation round per audit.
    if state.get("investigation_results"):
        return "report"

    if state.get("investigations"):
        return "investigate"

    return "report"