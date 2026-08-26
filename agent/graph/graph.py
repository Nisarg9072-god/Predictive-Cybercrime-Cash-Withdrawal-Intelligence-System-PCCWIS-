from langgraph.graph import StateGraph, START, END
from .state import InvestigationState
from . import nodes
from . import edges

def build_graph() -> StateGraph:
    """
    Builds the LangGraph for the cybercrime investigation agent.
    """
    workflow = StateGraph(InvestigationState)

    # Add Nodes
    workflow.add_node("INGEST_COMPLAINT", nodes.ingest_complaint)
    workflow.add_node("ANALYZE_COMPLAINT", nodes.analyze_complaint)
    workflow.add_node("FETCH_ACCOUNT", nodes.fetch_account)
    workflow.add_node("TRACE_TRANSACTIONS", nodes.trace_transactions)
    workflow.add_node("ASSESS_ACCOUNT_RISK", nodes.assess_account_risk)
    workflow.add_node("CHECK_WITHDRAWALS", nodes.check_withdrawals)
    workflow.add_node("GEO_ANALYSIS", nodes.geo_analysis)
    workflow.add_node("PREDICT_WITHDRAWAL", nodes.predict_withdrawal)
    workflow.add_node("VERIFY_EVIDENCE", nodes.verify_evidence)
    workflow.add_node("RISK_FUSION", nodes.risk_fusion)
    workflow.add_node("REPORT", nodes.report)
    workflow.add_node("AUDIT", nodes.audit)

    # Add Edges
    workflow.add_edge(START, "INGEST_COMPLAINT")
    workflow.add_edge("INGEST_COMPLAINT", "ANALYZE_COMPLAINT")
    workflow.add_edge("ANALYZE_COMPLAINT", "FETCH_ACCOUNT")
    workflow.add_edge("FETCH_ACCOUNT", "TRACE_TRANSACTIONS")
    workflow.add_edge("TRACE_TRANSACTIONS", "ASSESS_ACCOUNT_RISK")
    workflow.add_edge("ASSESS_ACCOUNT_RISK", "CHECK_WITHDRAWALS")
    workflow.add_edge("CHECK_WITHDRAWALS", "GEO_ANALYSIS")
    workflow.add_edge("GEO_ANALYSIS", "PREDICT_WITHDRAWAL")
    workflow.add_edge("PREDICT_WITHDRAWAL", "VERIFY_EVIDENCE")
    workflow.add_edge("VERIFY_EVIDENCE", "RISK_FUSION")
    
    # Conditional Routing
    workflow.add_conditional_edges(
        "RISK_FUSION",
        edges.decision_router,
        {
            "investigate_more": "FETCH_ACCOUNT",
            "report": "REPORT"
        }
    )

    workflow.add_edge("REPORT", "AUDIT")
    workflow.add_edge("AUDIT", END)

    return workflow

def get_compiled_graph():
    return build_graph().compile()
