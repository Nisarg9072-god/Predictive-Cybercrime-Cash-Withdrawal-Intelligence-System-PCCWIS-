from .graph.graph import get_compiled_graph
import uuid
import datetime
from database.repository import OperationalRepository, DatasetRepository
from database.queries import INSERT_SESSION, UPDATE_SESSION, INSERT_INVESTIGATION, UPDATE_INVESTIGATION

class PredictiveCybercrimeAgent:
    def __init__(self):
        self.graph = get_compiled_graph()

    def run(
        self,
        scenario_id: str,
        max_iterations: int = 15,
        max_tool_calls: int = 20,
        victim_name: str = "",
        victim_account_id: str = None,
    ):
        # 1. Load scenario
        scenario = DatasetRepository.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found in database.")
            
        session_id = str(uuid.uuid4())
        investigation_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        
        # Log to Operational DB
        OperationalRepository.execute_insert(
            INSERT_SESSION, 
            (session_id, now, "SCENARIO", scenario_id, "STARTED", now)
        )
        OperationalRepository.execute_insert(
            INSERT_INVESTIGATION,
            (investigation_id, session_id, "SCENARIO", scenario_id, scenario.description, "STARTED", now)
        )

        initial_state = {
            "session_id": session_id,
            "investigation_id": investigation_id,
            "scenario_id": scenario_id,
            "objective": f"Investigate {scenario_id} and determine laundering path and cash withdrawal risk.",
            "victim_name": victim_name or "",
            "victim_account_id": victim_account_id or "",
            "current_subject": victim_account_id if victim_account_id else None,
            "subjects_discovered": [],
            "accounts": [victim_account_id] if victim_account_id else [],
            "transactions": [],
            "transaction_chains": [],
            "profiles": [],
            "atms": [],
            "observations": [],
            "hypotheses": [],
            "evidence": [],
            "findings": [],
            "completed_tools": [],
            "pending_actions": [],
            "tool_args": {},
            "tool_history": [],
            "decision_history": [],
            "iteration": 1,
            "max_iterations": max_iterations,
            "confidence": None,
            "risk_score": None,
            "status": "INITIALIZED",
            "stop_reason": None
        }
        
        config = {"recursion_limit": max_tool_calls * 2}
        
        print(f"[AGENT] Starting investigation for {scenario_id}...")
        try:
            final_state = self.graph.invoke(initial_state, config=config)
            
            end_now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
            OperationalRepository.execute_update(UPDATE_SESSION, (end_now, "COMPLETED", 0, 0, None, session_id))
            OperationalRepository.execute_update(UPDATE_INVESTIGATION, (end_now, "COMPLETED", investigation_id))
            print("\n[REPORT] Investigation completed successfully.")
            return final_state
        except Exception as e:
            end_now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
            OperationalRepository.execute_update(UPDATE_SESSION, (end_now, "FAILED", 0, 0, str(e), session_id))
            OperationalRepository.execute_update(UPDATE_INVESTIGATION, (end_now, "FAILED", investigation_id))
            raise
