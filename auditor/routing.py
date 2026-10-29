from typing import Literal

from auditor.state import AuditState


def route_after_review(
    state: AuditState
) -> Literal["investigate", "report"]:

    if state["investigations"]:
        return "investigate"

    return "report"