from langgraph.graph import StateGraph, START, END
from .state import InvestigationState
from . import nodes
from . import edges

def build_graph() -> StateGraph:
    """
    Builds the dynamic LangGraph for the cybercrime investigation agent.
    """
    workflow = StateGraph(InvestigationState)

    # Add Nodes
    workflow.add_node("observe_node", nodes.observe_node)
    workflow.add_node("hypothesis_node", nodes.hypothesis_node)
    workflow.add_node("planner_node", nodes.planner_node)
    workflow.add_node("tool_execution_node", nodes.tool_execution_node)
    workflow.add_node("evaluate_node", nodes.evaluate_node)

    # Add Edges
    workflow.add_edge(START, "observe_node")
    workflow.add_edge("observe_node", "hypothesis_node")
    workflow.add_edge("hypothesis_node", "planner_node")
    workflow.add_edge("planner_node", "tool_execution_node")
    workflow.add_edge("tool_execution_node", "evaluate_node")
    
    # Conditional Routing
    workflow.add_conditional_edges(
        "evaluate_node",
        edges.decision_router,
        {
            "observe_node": "observe_node",
            "END": END
        }
    )

    return workflow

def get_compiled_graph():
    return build_graph().compile()
