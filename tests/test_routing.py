from auditor.routing import route_after_review
from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationType
)


def test_route_to_report():
    state = {
        "investigations": []
    }

    assert route_after_review(state) == "report"


def test_route_to_investigation():
    state = {
        "investigations": [
            InvestigationRequest(
                finding_title="Broken anchor",
                investigation_type=InvestigationType.ANCHOR,
                question="Does the link scroll to the correct section?",
                target="a[href='#talent-fake']"
            )
        ]
    }

    assert route_after_review(state) == "investigate"