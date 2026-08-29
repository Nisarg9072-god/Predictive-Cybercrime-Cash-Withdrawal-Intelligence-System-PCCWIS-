import uuid
import datetime
import json
from typing import Dict, Any, List
from .state import InvestigationState
from ..tools import registry
from ..llm_provider import LLMProvider
from risk.engine import RiskEngine
from database.repository import OperationalRepository
from database.queries import INSERT_OBSERVATION, INSERT_DECISION, INSERT_HYPOTHESIS, INSERT_FINDING, INSERT_AUDIT_EVENT
from evidence.collector import EvidenceCollector
from evidence.deduplicator import EvidenceDeduplicator

llm = LLMProvider(available=False)

def log_observation(state: InvestigationState, source: str, obs_type: str, summary: str, confidence: float = 1.0) -> Dict[str, Any]:
    obs_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
    obs_record = {
        "observation_id": obs_id, "investigation_id": state["investigation_id"],
        "source": source, "observation_type": obs_type, "summary": summary, "confidence": confidence, "created_at": now
    }
    try:
        OperationalRepository.execute_insert(INSERT_OBSERVATION, (obs_id, state["investigation_id"], source, obs_type, summary, confidence, now))
    except Exception:
        pass
    return obs_record

def log_decision(state: InvestigationState, tool: str, reason: str, result: str) -> Dict[str, Any]:
    dec_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
    dec_record = {
        "decision_id": dec_id, "investigation_id": state["investigation_id"], "iteration": state["iteration"],
        "observation_summary": "", "selected_tool": tool, "reason_summary": reason, "result_summary": result, "created_at": now
    }
    try:
        OperationalRepository.execute_insert(INSERT_DECISION, (dec_id, state["investigation_id"], state["iteration"], "", tool, reason, result, now))
    except Exception:
        pass
    return dec_record

def observe_node(state: InvestigationState) -> Dict[str, Any]:
    print(f"\nITERATION {state['iteration']}")
    print("[AGENT] Observing current state...")
    
    # Loop Detection
    recent_tools = [h.get("tool_name") for h in state.get("tool_history", [])][-3:]
    if len(recent_tools) == 3 and len(set(recent_tools)) == 1 and recent_tools[0] != "STOP":
        obs_summary = f"Loop detected on tool {recent_tools[0]}. Stopping investigation."
        print(f"Observation: {obs_summary}")
        return {"stop_reason": "AGENT_LOOP_DETECTED", "status": "OBSERVING"}
        
    if state["iteration"] >= state["max_iterations"]:
        obs_summary = "Maximum iterations reached."
        return {"stop_reason": "MAX_ITERATIONS_REACHED", "status": "OBSERVING"}

    obs_summary = ""
    if not state.get("accounts") and not state.get("current_subject"):
        obs_summary = f"Starting investigation for scenario {state['scenario_id']}. No accounts identified yet."
    elif state.get("accounts") and not state.get("transactions"):
        obs_summary = f"Account(s) {state['accounts']} identified. Checking for suspicious transactions."
    elif state.get("transactions") and not state.get("profiles"):
        obs_summary = f"Found {len(state['transactions'])} transactions. Need to analyze profiles."
    elif state.get("transactions") and state.get("profiles"):
        obs_summary = f"Identified accounts, profiles, and transactions. Continuing investigation."
    else:
        obs_summary = "Continuing investigation based on accumulated evidence."
    
    print(f"Observation: {obs_summary}")
    obs_record = log_observation(state, "observe_node", "STATE_SUMMARY", obs_summary)
    
    return {"observations": [obs_record], "status": "OBSERVING"}

def hypothesis_node(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Updating hypotheses...")
    new_hypotheses = []
    
    existing_desc = [h["description"] for h in state.get("hypotheses", [])]
    
    # ── Deterministic hypotheses ──────────────────────────────────────────────
    if state.get("accounts") and "Funds may have moved through multiple intermediary accounts." not in existing_desc:
        hyp_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        hyp_record = {
            "hypothesis_id": hyp_id, "investigation_id": state["investigation_id"],
            "description": "Funds may have moved through multiple intermediary accounts.", "category": "LAUNDERING",
            "confidence": 0.5, "status": "OPEN", "supporting_observations": "Accounts identified"
        }
        try:
            OperationalRepository.execute_insert(INSERT_HYPOTHESIS, (hyp_id, state["investigation_id"], hyp_record["description"], hyp_record["category"], hyp_record["confidence"], hyp_record["status"], hyp_record["supporting_observations"], now, now))
        except Exception:
            pass
        new_hypotheses.append(hyp_record)
        
    if state.get("transactions") and "A terminal cashout may be associated with the transaction chain." not in existing_desc:
        hyp_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        hyp_record = {
            "hypothesis_id": hyp_id, "investigation_id": state["investigation_id"],
            "description": "A terminal cashout may be associated with the transaction chain.", "category": "CASHOUT",
            "confidence": 0.5, "status": "OPEN", "supporting_observations": "Transactions identified"
        }
        try:
            OperationalRepository.execute_insert(INSERT_HYPOTHESIS, (hyp_id, state["investigation_id"], hyp_record["description"], hyp_record["category"], hyp_record["confidence"], hyp_record["status"], hyp_record["supporting_observations"], now, now))
        except Exception:
            pass
        new_hypotheses.append(hyp_record)

    # ── LLM-augmented hypothesis (only if LLM is available) ───────────────────
    llm_used, llm_hyp = llm.generate_hypothesis(state)
    if llm_used and isinstance(llm_hyp, dict) and "description" in llm_hyp:
        desc = llm_hyp["description"]
        if desc not in existing_desc and desc not in [h["description"] for h in new_hypotheses]:
            hyp_id = str(uuid.uuid4())
            now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
            hyp_record = {
                "hypothesis_id": hyp_id,
                "investigation_id": state["investigation_id"],
                "description": desc,
                "category": llm_hyp.get("category", "INFERRED"),
                "confidence": float(llm_hyp.get("confidence", 0.5)),
                "status": "OPEN",
                "supporting_observations": llm_hyp.get("reasoning", "LLM-generated"),
                "source": "LLM",
            }
            try:
                OperationalRepository.execute_insert(INSERT_HYPOTHESIS, (
                    hyp_id, state["investigation_id"], desc,
                    hyp_record["category"], hyp_record["confidence"],
                    hyp_record["status"], hyp_record["supporting_observations"], now, now
                ))
            except Exception:
                pass
            new_hypotheses.append(hyp_record)
        
    return {"hypotheses": new_hypotheses, "status": "HYPOTHESIZING"}

def planner_node(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Planning next action...")
    tool = "STOP"
    args = {}
    reason = "No actions available."

    ALL_TOOLS = [
        "get_scenario_raw", "get_mule_profiles", "search_transactions",
        "get_profile", "get_transaction_chain", "get_atm"
    ]
    completed = state.get("completed_tools", [])

    # ── Try LLM action ranking first ─────────────────────────────────────────
    llm_used, llm_tool = llm.rank_actions(state, [], [])
    if llm_used and llm_tool and llm_tool not in completed and llm_tool != "LLM_UNAVAILABLE":
        tool = llm_tool
        reason = "LLM selected action based on current investigation state."
        args = _build_args_for_tool(tool, state)
        print(f"[LLM] Suggested tool: {tool}")
    else:
        # ── Deterministic fallback ────────────────────────────────────────────
        if "get_scenario_raw" not in completed:
            tool = "get_scenario_raw"
            args = {"scenario_id": state["scenario_id"]}
            reason = "Need to load scenario context."
        elif state.get("current_subject") == "MULE_SEARCH_NEEDED" and "get_mule_profiles" not in completed:
            tool = "get_mule_profiles"
            args = {}
            reason = "No explicit victim account. Finding known mules."
        elif not state.get("accounts") and state.get("current_subject") and state.get("current_subject") != "MULE_SEARCH_NEEDED":
            tool = "search_transactions"
            args = {"from_account": state["current_subject"]}
            reason = "Searching transactions for the primary subject."
        elif state.get("accounts"):
            unprofiled = [acc for acc in state["accounts"] if not any(p.get("account_id") == acc for p in state.get("profiles", []))]
            if unprofiled:
                tool = "get_profile"
                args = {"identifier": unprofiled[0]}
                reason = f"Analysing profile for account {unprofiled[0]}."
            elif not state.get("transactions") and "search_transactions" not in completed:
                tool = "search_transactions"
                args = {"from_account": state["accounts"][0]}
                reason = "Searching transactions from discovered account."
            elif state.get("transactions") and not state.get("transaction_chains"):
                tool = "get_transaction_chain"
                args = {"chain_id": state["transactions"][0].get("chain_id") or state["transactions"][0]["txn_id"]}
                reason = "Tracing transaction chain from first transaction."
            elif state.get("transaction_chains"):
                terminal_atms = [c.get("atm_id") for c in state.get("transaction_chains", []) if c.get("atm_id")]
                uninvestigated_atms = [a for a in terminal_atms if not any(atm.get("atm_id") == a for atm in state.get("atms", []))]
                if uninvestigated_atms:
                    tool = "get_atm"
                    args = {"atm_id": uninvestigated_atms[0]}
                    reason = f"Analysing terminal ATM {uninvestigated_atms[0]}."
                else:
                    tool = "STOP"
                    reason = "Sufficient evidence gathered."
            else:
                tool = "STOP"
                reason = "No transactions found, stopping investigation."
        else:
            tool = "STOP"
            reason = "Insufficient information to proceed."

    print(f"Decision: {reason}")
    print(f"Tool: {tool}")

    dec_record = log_decision(state, tool, reason, "PENDING")
    return {"pending_actions": [tool], "tool_args": args, "decision_history": [dec_record], "status": "PLANNING"}


def _build_args_for_tool(tool: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Build default args for a tool given current state."""
    if tool == "get_scenario_raw":
        return {"scenario_id": state["scenario_id"]}
    if tool == "search_transactions" and state.get("accounts"):
        return {"from_account": state["accounts"][0]}
    if tool == "get_profile" and state.get("accounts"):
        return {"identifier": state["accounts"][0]}
    if tool == "get_transaction_chain" and state.get("transactions"):
        return {"chain_id": state["transactions"][0].get("chain_id") or state["transactions"][0].get("txn_id", "")}
    if tool == "get_mule_profiles":
        return {}
    if tool == "get_atm" and state.get("transaction_chains"):
        for c in state["transaction_chains"]:
            if isinstance(c, dict) and c.get("atm_id"):
                return {"atm_id": c["atm_id"]}
    return {}

def tool_execution_node(state: InvestigationState) -> Dict[str, Any]:
    tool_name = state.get("pending_actions", ["STOP"])[0]
    args = state.get("tool_args", {})
    print(f"[AGENT] Executing {tool_name} with {args}...")
    
    start_time = datetime.datetime.now()
    if tool_name == "STOP":
        exec_time = (datetime.datetime.now() - start_time).total_seconds()
        result_record = {"success": True, "tool_name": "STOP", "data": "STOP", "execution_time": exec_time, "iteration": state["iteration"]}
        return {"status": "EXECUTED", "tool_history": [result_record], "completed_tools": ["STOP"]}
        
    if hasattr(registry, tool_name):
        tool_func = getattr(registry, tool_name)
        try:
            res = tool_func(**args)
            exec_time = (datetime.datetime.now() - start_time).total_seconds()
            result_record = res.model_dump()
            result_record["tool_name"] = tool_name
            result_record["execution_time"] = exec_time
            result_record["iteration"] = state["iteration"]
            return {"status": "EXECUTED", "tool_history": [result_record], "completed_tools": [tool_name]}
        except Exception as e:
            exec_time = (datetime.datetime.now() - start_time).total_seconds()
            result_record = {"success": False, "tool_name": tool_name, "error": str(e), "execution_time": exec_time, "iteration": state["iteration"]}
            return {"status": "EXECUTED", "tool_history": [result_record], "completed_tools": [tool_name]}
    
    exec_time = (datetime.datetime.now() - start_time).total_seconds()
    result_record = {"success": False, "tool_name": tool_name, "error": "Tool not found", "execution_time": exec_time, "iteration": state["iteration"]}
    return {"status": "EXECUTED", "tool_history": [result_record], "completed_tools": [tool_name]}

def evaluate_node(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Evaluating tool result...")
    updates = {"iteration": state["iteration"] + 1, "status": "EVALUATED"}
    
    if not state.get("tool_history"):
        return updates
        
    result = state["tool_history"][-1]
    
    if result.get("tool_name") == "STOP":
        updates["stop_reason"] = "AGENT_DECIDED_STOP"
        return updates
        
    evidence_list = []
    
    if result.get("success"):
        data = result.get("data")
        tool = result.get("tool_name")
        investigation_id = state.get("investigation_id", "unknown")
        
        now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        
        if tool == "get_scenario_raw" and data:
            try:
                data_obj = {}
                if "data_json" in data and data["data_json"]:
                    if isinstance(data["data_json"], str):
                        data_obj = json.loads(data["data_json"])
                    else:
                        data_obj = data["data_json"]
                        
                entities = data_obj.get("identified_entities", {})
                accs = []
                if "primary_victim_account" in entities:
                    accs.append(entities["primary_victim_account"])
                if "suspect_accounts" in entities:
                    if isinstance(entities["suspect_accounts"], list):
                        accs.extend(entities["suspect_accounts"])
                
                if accs:
                    if not state.get("accounts"):
                        updates["accounts"] = accs
                    updates["current_subject"] = accs[0]
                else:
                    updates["current_subject"] = "MULE_SEARCH_NEEDED"
            except Exception as e:
                updates["current_subject"] = "MULE_SEARCH_NEEDED"
                
            items = EvidenceCollector.from_scenario(investigation_id, data.get("scenario_id", "UNKNOWN"), data_obj if 'data_obj' in locals() else {})
            evidence_list.extend(items)
            
        elif tool == "get_mule_profiles" and data:
            if isinstance(data, list) and len(data) > 0:
                acc = data[0]["account_id"]
                if acc not in state.get("accounts", []):
                    updates["accounts"] = [acc]
                updates["current_subject"] = acc
                items = EvidenceCollector.from_mule_profiles(investigation_id, data)
                evidence_list.extend(items)
                
        elif tool == "search_transactions" and data:
            if isinstance(data, list):
                updates["transactions"] = data
                new_accounts = []
                for t in data:
                    to_acc = t.get("to_account_id")
                    if to_acc and to_acc not in state.get("accounts", []):
                        new_accounts.append(to_acc)
                if new_accounts:
                    updates["accounts"] = new_accounts
                items = EvidenceCollector.from_transactions(investigation_id, data)
                evidence_list.extend(items)
            
        elif tool == "get_profile" and data:
            updates["profiles"] = [data]
            items = EvidenceCollector.from_profile(investigation_id, data)
            evidence_list.extend(items)
            
        elif tool == "get_transaction_chain" and data:
            if isinstance(data, list) and len(data) > 0:
                # Create a proper chain summary since data is a list of transactions
                chain_summary = {
                    "chain_id": data[0].get("chain_id", "CHAIN_UNKNOWN"),
                    "pattern_type": data[0].get("pattern_type", "unknown"),
                    "total_amount": sum(d.get("amount_inr", 0) for d in data),
                    "hop_count": max((d.get("hop_layer", 0) for d in data), default=0),
                    "transactions": data
                }
                updates["transaction_chains"] = [chain_summary]
                updates["transactions"] = data  # Ensure RiskEngine sees the individual transactions
                items = EvidenceCollector.from_chain(investigation_id, data)
                evidence_list.extend(items)
                
        elif tool == "get_atm" and data is not None:
            # ATM table may be malformed — check if result is valid
            updates["atms"] = [data]
            items = EvidenceCollector.from_atm(investigation_id, data)
            evidence_list.extend(items)
        elif tool == "get_atm" and data is None:
            # ATM table is malformed (known dataset corruption) — log BLOCKED observation
            log_observation(state, "evaluate_node", "ATM_ANALYSIS_BLOCKED",
                "ATM data is inaccessible due to known dataset corruption. ATM analysis BLOCKED.", confidence=1.0)
            print("[BLOCKED] ATM table malformed — skipping ATM analysis. Investigation continues.")

    if evidence_list:
        # Deduplicate evidence
        # State stores evidence as dicts currently, we need to convert back to EvidenceItem or just use dicts.
        # But wait, EvidenceDeduplicator takes List[EvidenceItem].
        # In state, we can store the raw dicts, but deduplicate using the hashes.
        # Let's just persist the new ones to the DB, and add them to state if they are new.
        repo = OperationalRepository()
        new_evidence_dicts = []
        for item in evidence_list:
            repo.save_evidence(item)
            new_evidence_dicts.append(item.to_db_dict())
        
        # We append to state evidence
        # We should probably deduplicate them across state, but storing everything is fine for now as RiskEngine takes state["evidence"]
        updates["evidence"] = new_evidence_dicts
    
    # Risk Engine Finding
    temp_state = {**state, **updates}
    temp_state["accounts"] = state.get("accounts", []) + updates.get("accounts", [])
    temp_state["profiles"] = state.get("profiles", []) + updates.get("profiles", [])
    temp_state["transactions"] = state.get("transactions", []) + updates.get("transactions", [])
    temp_state["transaction_chains"] = state.get("transaction_chains", []) + updates.get("transaction_chains", [])
    temp_state["atms"] = state.get("atms", []) + updates.get("atms", [])
    temp_state["evidence"] = state.get("evidence", []) + updates.get("evidence", [])
    
    finding = RiskEngine.generate_finding(temp_state)
    if finding:
        existing_titles = [f["title"] for f in state.get("findings", [])]
        if finding["title"] not in existing_titles:
            # LLM finding explanation (does not change risk values)
            ev_for_llm = temp_state.get("evidence", [])[:8]
            llm_used, explanation = llm.generate_executive_summary(
                {"scenario_id": state.get("scenario_id", ""), "scenario_name": "",
                 "crime_category": "", "victim_city": "", "victim_state": "", "amount_lost_inr": 0},
                [finding], {"risk_score": 0, "risk_level": ""}, []
            ) if False else (False, None)  # Reserve for report stage, not per-finding
            # Use targeted finding explanation instead
            llm_used_f, explanation_f = llm.summarize_evidence(ev_for_llm)
            if llm_used_f:
                finding["llm_explanation"] = explanation_f

            updates["findings"] = [finding]
            now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
            try:
                OperationalRepository.execute_insert(INSERT_FINDING, (
                    finding["finding_id"], state["investigation_id"], finding["title"], finding["category"], finding["severity"],
                    finding["confidence"], finding["description"], str(finding["evidence_ids"]), finding["remediation"], finding["status"], now
                ))
            except Exception:
                pass
                
    # Evaluate Risk Score & Log Assessment
    analysis = RiskEngine.calculate_risk(temp_state)
    assessment_id = str(uuid.uuid4())
    indicator_ids = ",".join([ind["indicator_id"] for ind in analysis["indicators"]])
    evidence_ids = ",".join([e["evidence_id"] for e in temp_state.get("evidence", [])])
    
    try:
        now = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        OperationalRepository.log_risk_assessment({
            "risk_assessment_id": assessment_id,
            "investigation_id": state.get("investigation_id", "unknown"),
            "iteration": state["iteration"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "confidence": analysis["confidence"],
            "indicator_ids": indicator_ids,
            "evidence_ids": evidence_ids,
            "created_at": now
        })
    except Exception as e:
        print(f"[EVALUATE] Failed to log risk assessment: {e}")
        pass
            
    return updates
