from .state import InvestigationState
from typing import Literal

def decision_router(state: InvestigationState) -> Literal["observe_node", "END"]:
    """
    Routes the agent to the next step based on the state.
    """
    print("[AGENT] Making routing decision...")
    
    if state.get("stop_reason"):
        print(f"Stopping investigation: {state['stop_reason']}")
        return "END"
        
    # Check budget fallback
    if state.get("iteration", 0) >= state.get("max_iterations", 15):
        print("Stopping investigation: MAX_ITERATIONS_REACHED")
        return "END"
        
    return "observe_node"
