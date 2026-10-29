from langgraph.graph import StateGraph, START, END

from auditor.state import AuditState
from auditor.nodes.capture import capture_page
from auditor.nodes.lighthouse import run_lighthouse
from auditor.nodes.accessibility import run_axe
from auditor.nodes.analysis import analyse_page
from auditor.nodes.report import generate_report
from auditor.nodes.evidence import prepare_evidence

from auditor.nodes.accessibility_analysis import (
    analyse_accessibility
)
from auditor.nodes.seo_analysis import analyse_seo
from auditor.nodes.ux_analysis import analyse_ux
from auditor.nodes.analysis import analyse_page
from auditor.nodes.report import generate_report
from auditor.nodes.review import review_findings


def build_graph(
    lighthouse_node=run_lighthouse,
    axe_node=run_axe,
    accessibility_node=analyse_accessibility,
    seo_node=analyse_seo,
    ux_node=analyse_ux,
    review_node=None
):
    builder = StateGraph(AuditState)

    # Register nodes
    builder.add_node("capture", capture_page)
    builder.add_node("lighthouse", lighthouse_node)
    builder.add_node("axe", axe_node)
    builder.add_node("prepare_evidence", prepare_evidence)

    builder.add_node(
        "accessibility_analysis",
        accessibility_node
    )
    builder.add_node("seo_analysis", seo_node)
    builder.add_node("ux_analysis", ux_node)

    builder.add_node("analyse", analyse_page)
    builder.add_node("report", generate_report)
    builder.add_node("review", review_node or review_findings)

    # Capture
    builder.add_edge(START, "capture")

    # Parallel automated audits
    builder.add_edge("capture", "lighthouse")
    builder.add_edge("capture", "axe")

    # Wait for both automated audits
    builder.add_edge(
        ["lighthouse", "axe"],
        "prepare_evidence"
    )

    # Parallel AI analysis
    builder.add_edge(
        "prepare_evidence",
        "accessibility_analysis"
    )
    builder.add_edge(
        "prepare_evidence",
        "seo_analysis"
    )
    builder.add_edge(
        "prepare_evidence",
        "ux_analysis"
    )

    # Wait for all three analysts
    builder.add_edge(
        [
            "accessibility_analysis",
            "seo_analysis",
            "ux_analysis"
        ],
        "analyse"
    )

    # Aggregate and report
    builder.add_edge("analyse", "review")
    builder.add_edge("review", "report")
    builder.add_edge("report", END)

    return builder.compile()