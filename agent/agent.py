from .graph.graph import get_compiled_graph

class PredictiveCybercrimeAgent:
    def __init__(self):
        self.graph = get_compiled_graph()

    def run(self, case_id: str):
        initial_state = {
            "case_id": case_id,
            "complaint": {},
            "current_account": None,
            "investigated_accounts": [],
            "transaction_paths": [],
            "suspicious_accounts": [],
            "withdrawal_candidates": [],
            "predictions": [],
            "evidence": [],
            "risk_score": None,
            "confidence": None,
            "tool_calls": [],
            "alerts": [],
            "errors": [],
            "investigation_status": "INITIALIZED",
            "iteration_count": 0
        }
        
        # In a real environment, you might use an async runtime, limit recursion depth etc.
        config = {"recursion_limit": 20}
        
        print(f"[AGENT] Starting investigation for {case_id}...")
        for event in self.graph.stream(initial_state, config=config):
            for k, v in event.items():
                pass # The nodes will print out messages, or we could handle streamed state here
        
        # We can fetch the final state from the agent memory if we configured a checkpointer,
        # but for this mock sync loop we just let it finish.
        print("[REPORT] Investigation completed.")
