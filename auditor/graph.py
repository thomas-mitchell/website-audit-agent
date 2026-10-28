from langgraph.graph import StateGraph, START, END

from auditor.state import AuditState
from auditor.nodes.capture import capture_page
from auditor.nodes.analysis import analyse_page
from auditor.nodes.report import generate_report


def build_graph():
    builder = StateGraph(AuditState)

    # Register nodes
    builder.add_node("capture", capture_page)
    builder.add_node("analyse", analyse_page)
    builder.add_node("report", generate_report)

    # Define execution flow
    builder.add_edge(START, "capture")
    builder.add_edge("capture", "analyse")
    builder.add_edge("analyse", "report")
    builder.add_edge("report", END)

    return builder.compile()