from langgraph.graph import StateGraph, START, END

from auditor.state import AuditState
from auditor.nodes.capture import capture_page
from auditor.nodes.lighthouse import run_lighthouse
from auditor.nodes.accessibility import run_axe
from auditor.nodes.analysis import analyse_page
from auditor.nodes.report import generate_report


def build_graph(
    lighthouse_node=run_lighthouse,
    axe_node=run_axe
):
    builder = StateGraph(AuditState)

    builder.add_node("capture", capture_page)
    builder.add_node("lighthouse", lighthouse_node)
    builder.add_node("axe", axe_node)
    builder.add_node("analyse", analyse_page)
    builder.add_node("report", generate_report)

    builder.add_edge(START, "capture")
    builder.add_edge("capture", "lighthouse")
    builder.add_edge("capture", "axe")
    builder.add_edge(["lighthouse", "axe"], "analyse")
    builder.add_edge("analyse", "report")
    builder.add_edge("report", END)

    return builder.compile()