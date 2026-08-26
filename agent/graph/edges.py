from .state import InvestigationState
from typing import Literal

def decision_router(state: InvestigationState) -> Literal["investigate_more", "report"]:
    """
    Routes the agent to the next step based on the state.
    """
    print("[AGENT] Making routing decision...")
    # Mock logic: if we have predictions, we can report.
    if state.get("predictions"):
        return "report"
    return "investigate_more"
