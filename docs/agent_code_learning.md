# Agent Code Learning Guide

> **PCCWIS — Learning-Oriented Implementation Reference**
> For developers who understand Python and are learning agentic AI.

---

## Table of Contents

1. [What Is an AI Agent?](#1-what-is-an-ai-agent)
2. [What Makes PCCWIS Agentic?](#2-what-makes-pccwis-agentic)
3. [LLM vs ML Model vs Agent](#3-llm-vs-ml-model-vs-agent)
4. [Tool Calling](#4-tool-calling)
5. [Structured Outputs](#5-structured-outputs)
6. [State](#6-state)
7. [Memory](#7-memory)
8. [Short-Term Investigation State](#8-short-term-investigation-state)
9. [Long-Term Knowledge](#9-long-term-knowledge)
10. [Agent Loop](#10-agent-loop)
11. [Planning](#11-planning)
12. [Replanning](#12-replanning)
13. [Tool Selection](#13-tool-selection)
14. [Guardrails](#14-guardrails)
15. [Deterministic vs Probabilistic Decisions](#15-deterministic-vs-probabilistic-decisions)
16. [Human Approval](#16-human-approval)
17. [Error Handling](#17-error-handling)
18. [Retry Logic](#18-retry-logic)
19. [Observability](#19-observability)
20. [Evaluation](#20-evaluation)
21. [Tool Implementations](#21-tool-implementations)
22. [Minimal Conceptual Agent](#22-minimal-conceptual-agent)
23. [Evolution to LangGraph](#23-evolution-to-langgraph)

---

## 1. What Is an AI Agent?

An **AI agent** is a system that:
1. **Perceives** its environment (reads state, gets inputs)
2. **Reasons** about what to do next (uses an LLM or rules)
3. **Acts** in its environment (calls tools, modifies state)
4. **Repeats** until a goal is achieved

**Analogy:** Think of it like a junior detective:
- A junior detective does NOT know everything upfront
- They gather one piece of evidence at a time
- Each clue tells them what to look for next
- They stop when they have enough to file a report

An AI agent does the same thing — but programmatically, in seconds.

**Key difference from a simple API call:**

```python
# NOT an agent — single shot
result = model.predict(complaint_data)  # One call, done

# IS an agent — multi-step reasoning loop
while not investigation_complete():
    observation = observe_current_state()
    next_action = reason_and_plan(observation)
    result = execute_action(next_action)
    update_state(result)
```

---

## 2. What Makes PCCWIS Agentic?

PCCWIS is agentic because:

| Property | How PCCWIS implements it |
|---|---|
| **Multi-step decision-making** | Agent decides which account to investigate next based on what was found |
| **Tool use** | Agent calls 14+ specialized tools — graph DB, ML models, geospatial APIs |
| **State accumulation** | Investigation state grows with each tool call |
| **Adaptive planning** | Finding a fan-out pattern changes the next steps |
| **Goal-directed** | Agent stops when prediction is ready — not after a fixed number of steps |
| **Controlled autonomy** | Scope limits prevent unbounded investigation |

---

## 3. LLM vs ML Model vs Agent

This is the most important distinction in PCCWIS:

| Component | Role | Example |
|---|---|---|
| **LLM** | Reasoning, planning, explanation, report writing | "Given these findings, I should next trace M001's outgoing transactions" |
| **ML Model** | Numerical prediction, risk scoring, fraud classification | FraudClassifier outputs `fraud_probability: 0.91` |
| **Agent** | Orchestrates LLM + ML + Tools in a loop | LangGraph StateGraph runs the OODA loop |

> **The LLM NEVER does this:**
> ```python
> # WRONG — LLM should NOT compute risk scores
> risk = llm.ask("What is the risk score for account M001?")
> ```

> **The LLM ALWAYS does this:**
> ```python
> # CORRECT — LLM decides what to investigate next
> next_tool = llm.ask("Given the current evidence, what should I investigate next?")
> risk = tools.calculate_account_risk("M001", features)  # ML model does the math
> ```

**Why?** LLMs are excellent at language, reasoning, and planning — but they are not calibrated numerical predictors. A financial crime prediction system must be **auditable, reproducible, and numerically calibrated**. LLMs are none of these for numerical tasks.

---

## 4. Tool Calling

**Tool calling** (also called "function calling") is the mechanism by which an LLM selects and invokes structured functions.

### How it works conceptually:

```python
# You define tools with a schema
tools = [
    {
        "name": "get_transactions",
        "description": "Retrieve transactions for an account",
        "parameters": {
            "account_id": {"type": "string", "required": True},
            "direction": {"type": "string", "enum": ["incoming", "outgoing", "all"]},
            "limit": {"type": "integer", "default": 20}
        }
    },
    # ... more tools
]

# LLM receives tools list and current state
# LLM outputs a tool call (not free text)
response = llm.chat(
    messages=[{"role": "user", "content": current_investigation_context}],
    tools=tools
)

# Parse tool call
if response.tool_calls:
    tool_name = response.tool_calls[0].name  # e.g. "get_transactions"
    tool_args = response.tool_calls[0].arguments  # e.g. {"account_id": "M001"}

    # Execute the actual tool (not LLM — real code)
    result = execute_tool(tool_name, tool_args)
```

### PCCWIS Tool Calling Pattern

```python
from typing import Optional
from pydantic import BaseModel

class ToolCall(BaseModel):
    tool_name: str
    tool_args: dict
    reasoning: str  # Why this tool was chosen

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Optional[dict]
    error: Optional[str]
    execution_time_ms: int
```

---

## 5. Structured Outputs

Instead of asking the LLM to return free-text, we ask it to return **structured JSON** that matches a defined schema.

**Why?** Because downstream code needs to reliably parse the LLM's decisions.

```python
from pydantic import BaseModel
from typing import Literal, Optional

class InvestigationDecision(BaseModel):
    """Structured decision output from the LLM reasoning step"""
    next_action: Literal["call_tool", "verify_evidence", "generate_report", "escalate_human", "abort"]
    tool_name: Optional[str]  # Which tool to call
    tool_args: Optional[dict]  # Tool arguments
    reasoning: str            # Why this decision was made (for audit)
    evidence_gaps: list[str]  # What is still unknown
    scope_check_passed: bool  # Did we verify scope limits?
```

The LLM is instructed to always return a `InvestigationDecision` object. This prevents hallucinated free-text responses from breaking the agent loop.

---

## 6. State

**State** is the agent's memory within a single investigation. It holds everything the agent has discovered so far.

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InvestigationState(BaseModel):
    """Complete state for one investigation run"""

    # --- Investigation metadata ---
    investigation_id: str
    complaint_id: str
    started_at: datetime
    agent_run_id: str

    # --- Scope limits (enforced) ---
    max_graph_depth: int = 5
    max_tool_calls: int = 100
    max_accounts_investigated: int = 50
    max_investigation_time_minutes: int = 30

    # --- Progress tracking ---
    tool_calls_made: int = 0
    graph_depth_reached: int = 0
    accounts_investigated: list[str] = Field(default_factory=list)
    tool_call_log: list[dict] = Field(default_factory=list)

    # --- Complaint data ---
    complaint: Optional[dict] = None
    victim_account: Optional[dict] = None
    fraud_amount: Optional[float] = None

    # --- Investigation findings ---
    traced_accounts: list[dict] = Field(default_factory=list)
    traced_transactions: list[dict] = Field(default_factory=list)
    suspicious_paths: list[dict] = Field(default_factory=list)
    flags_raised: list[str] = Field(default_factory=list)

    # --- ML results ---
    account_risk_scores: dict[str, float] = Field(default_factory=dict)
    fraud_probabilities: dict[str, float] = Field(default_factory=dict)
    anomaly_scores: dict[str, float] = Field(default_factory=dict)

    # --- Geographic data ---
    withdrawal_history: list[dict] = Field(default_factory=list)
    atm_locations: list[dict] = Field(default_factory=list)
    geographic_risk_scores: dict[str, float] = Field(default_factory=dict)

    # --- Prediction results ---
    withdrawal_prediction: Optional[dict] = None
    fused_risk_score: Optional[float] = None
    risk_level: Optional[str] = None

    # --- Final outputs ---
    report: Optional[str] = None
    alert_id: Optional[str] = None
    investigation_status: str = "IN_PROGRESS"
    human_approval_required: bool = False
    human_approval_status: Optional[str] = None
```

---

## 7. Memory

In agentic AI, "memory" has two types:

| Type | Description | PCCWIS Implementation |
|---|---|---|
| **Short-term / Working memory** | State within the current investigation | `InvestigationState` (in-memory + Redis) |
| **Long-term / Episodic memory** | Knowledge from past investigations | Database + model training data |

---

## 8. Short-Term Investigation State

The `InvestigationState` is the agent's working memory for one investigation. It is:

- **Initialized** when the investigation starts
- **Updated** after every tool call
- **Persisted** to Redis for recovery if the agent crashes
- **Closed** when the investigation completes

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

def save_state(state: InvestigationState):
    """Persist investigation state to Redis for crash recovery"""
    key = f"investigation:{state.investigation_id}"
    redis_client.set(key, state.json(), ex=3600)  # 1 hour TTL

def load_state(investigation_id: str) -> Optional[InvestigationState]:
    """Recover investigation state from Redis"""
    key = f"investigation:{investigation_id}"
    data = redis_client.get(key)
    if data:
        return InvestigationState.parse_raw(data)
    return None
```

---

## 9. Long-Term Knowledge

Long-term knowledge is NOT stored in the LLM's weights. It is stored in:

| Knowledge Type | Storage | Access |
|---|---|---|
| Complaint history | PostgreSQL | `get_complaint()` tool |
| Account profiles | PostgreSQL | `get_account()` tool |
| Transaction history | PostgreSQL + Neo4j | `get_transactions()` tool |
| Historical withdrawal patterns | PostgreSQL | `get_withdrawal_history()` tool |
| ML model weights | File system / MLflow | ML service |
| ATM geographic data | PostgreSQL + PostGIS | `get_atm_locations()` tool |
| Historical cybercrime density | PostgreSQL | `get_geographic_risk()` tool |

The LLM can ONLY access long-term knowledge through the authorized tool APIs.

---

## 10. Agent Loop

The core agent loop in plain Python (conceptual):

```python
def run_investigation(complaint_id: str) -> InvestigationState:
    """Main investigation agent loop"""

    # Initialize state
    state = InvestigationState(
        investigation_id=generate_id(),
        complaint_id=complaint_id,
        started_at=datetime.now(),
        agent_run_id=generate_id()
    )

    # Save initial state
    save_state(state)
    record_audit_event(state.investigation_id, "INVESTIGATION_STARTED")

    # OODA loop
    while not is_investigation_complete(state):

        # --- OBSERVE ---
        observation = build_observation(state)

        # --- REASON + PLAN ---
        decision = llm_decide_next_action(observation, state)

        # Check if LLM wants to stop
        if decision.next_action == "generate_report":
            break
        if decision.next_action == "abort":
            state.investigation_status = "ABORTED"
            break
        if decision.next_action == "escalate_human":
            state.human_approval_required = True
            save_state(state)
            return state  # Pause for human input

        # --- ACT ---
        if decision.next_action == "call_tool":
            result = call_tool_with_retry(
                tool_name=decision.tool_name,
                tool_args=decision.tool_args,
                state=state
            )
            # Update state
            state = update_state_with_result(state, decision.tool_name, result)
            state.tool_calls_made += 1

        # Enforce scope limits
        if exceeds_scope_limits(state):
            break

        save_state(state)

    # --- VERIFY + PREDICT + DECIDE ---
    if state.investigation_status != "ABORTED":
        state = verify_and_predict(state)
        state = apply_risk_decision(state)

    # --- REPORT + ALERT ---
    state.report = generate_report(state)
    if should_alert(state):
        state.alert_id = create_alert(state)

    record_audit_event(state.investigation_id, "INVESTIGATION_COMPLETE")
    state.investigation_status = "COMPLETE"
    save_state(state)
    return state


def is_investigation_complete(state: InvestigationState) -> bool:
    """Check all stop conditions"""
    if state.tool_calls_made >= state.max_tool_calls:
        return True
    if state.graph_depth_reached >= state.max_graph_depth:
        return True
    if len(state.accounts_investigated) >= state.max_accounts_investigated:
        return True
    elapsed = (datetime.now() - state.started_at).total_seconds() / 60
    if elapsed >= state.max_investigation_time_minutes:
        return True
    return False
```

---

## 11. Planning

Planning is when the LLM decides the next sequence of steps:

```python
def llm_decide_next_action(
    observation: dict,
    state: InvestigationState
) -> InvestigationDecision:
    """Ask LLM to plan the next action"""

    system_prompt = """
    You are a financial crime investigation agent. 
    
    RULES:
    1. You orchestrate the investigation. You do NOT compute fraud scores.
    2. Always use tools to retrieve data. Never assume or invent data.
    3. Check scope limits before planning more steps.
    4. When sufficient evidence is gathered, choose 'generate_report'.
    5. If risk score indicates CRITICAL, choose 'escalate_human'.
    6. You MUST return a valid InvestigationDecision JSON object.
    
    AVAILABLE TOOLS: [list of tool names and descriptions]
    
    SCOPE STATUS: Tool calls: {tool_calls}/{max_tool_calls}, 
                  Graph depth: {depth}/{max_depth}
    """

    user_message = f"""
    Current investigation observation:
    {json.dumps(observation, indent=2)}
    
    What should I do next? Return a valid InvestigationDecision.
    """

    response = llm.chat(
        messages=[
            {"role": "system", "content": system_prompt.format(...)},
            {"role": "user", "content": user_message}
        ],
        response_format=InvestigationDecision  # Enforce structured output
    )

    return InvestigationDecision.parse_raw(response.content)
```

---

## 12. Replanning

Replanning occurs when the agent finds something unexpected:

```python
# Example: Agent planned to investigate M001's recipients
# But finds that M001 has 20+ recipients (fan-out fraud)
# Agent must replan: prioritize top 5 by amount

def should_replan(state: InvestigationState, latest_result: dict) -> bool:
    """Check if new findings require a change in investigation strategy"""
    
    # Fan-out detected — prioritize
    if latest_result.get("recipient_count", 0) > 10:
        state.flags_raised.append("LARGE_FAN_OUT")
        return True
    
    # High-risk account found — prioritize withdrawal history
    if latest_result.get("risk_score", 0) > 85:
        return True
    
    return False
```

---

## 13. Tool Selection

The LLM selects tools based on:
1. What is currently known (observation)
2. What is still unknown (evidence gaps)
3. What tools are available (tool schema)
4. What scope remains (limits)

**Tool selection guidance embedded in system prompt:**

```
Investigation priority order:
1. Fetch complaint → fetch victim account (always first)
2. Trace outgoing transactions from victim (discover mule accounts)
3. For each mule: calculate risk, detect anomalies
4. Get withdrawal history for high-risk accounts
5. Get ATM locations and geographic risk
6. Predict withdrawal location (ML)
7. Fuse risk → decide → report/alert

Skip steps only if scope limits are near exhaustion.
Never call predict_withdrawal_location without first getting withdrawal history.
```

---

## 14. Guardrails

Guardrails prevent the agent from doing harmful things:

```python
class ToolGuardrail:
    """Enforces safety controls on tool calls"""

    DANGEROUS_TOOLS = ["modify_account", "freeze_account", "send_external_alert"]
    HUMAN_REQUIRED_TOOLS = ["freeze_account", "send_external_alert"]

    def check(self, tool_name: str, tool_args: dict, state: InvestigationState) -> bool:
        """Returns True if tool call is allowed"""

        # Block dangerous tools entirely
        if tool_name in self.DANGEROUS_TOOLS:
            raise ToolNotPermittedError(f"Tool {tool_name} not permitted for agent")

        # Block if scope limits exceeded
        if state.tool_calls_made >= state.max_tool_calls:
            raise ScopeLimitError("Max tool calls exceeded")

        # Block financial write operations
        if tool_args.get("write_operation"):
            raise ToolNotPermittedError("Agent cannot perform write operations")

        # Block if account already investigated
        account_id = tool_args.get("account_id")
        if account_id and account_id in state.accounts_investigated:
            # Allow but log — prevent redundant calls
            pass

        return True
```

---

## 15. Deterministic vs Probabilistic Decisions

Understanding which parts of the system are deterministic vs probabilistic:

| Decision | Type | Example |
|---|---|---|
| "Has the max tool call limit been reached?" | **Deterministic** | `tool_calls >= 100` → always True or False |
| "What should I investigate next?" | **Probabilistic** (LLM) | Depends on model, temperature, context |
| "What is the fraud probability?" | **Probabilistic** (ML) | `XGBoost.predict_proba()` → [0, 1] |
| "Is the risk score above threshold?" | **Deterministic** | `score >= 80` → always True or False |
| "Should I escalate to human?" | **Deterministic** | Based on `risk_level == "CRITICAL"` |

**Rule:** All numerical thresholds and scope limits must be **deterministic**. The LLM makes investigation planning decisions, which are probabilistic — but we constrain them with deterministic guardrails.

---

## 16. Human Approval

```python
def check_human_approval_required(state: InvestigationState) -> bool:
    """Deterministic check — not LLM decision"""
    if state.fused_risk_score and state.fused_risk_score >= 80:
        return True
    if state.risk_level in ["CRITICAL", "EXTREME"]:
        return True
    return False


def pause_for_human_approval(state: InvestigationState) -> InvestigationState:
    """Pause investigation and wait for human input"""
    state.human_approval_required = True
    state.investigation_status = "AWAITING_HUMAN_APPROVAL"
    save_state(state)
    
    # Notify dashboard (via event queue)
    publish_event("HUMAN_APPROVAL_REQUIRED", {
        "investigation_id": state.investigation_id,
        "risk_score": state.fused_risk_score,
        "report_summary": summarize_evidence(state)
    })
    
    # Agent pauses here — resumes when human_approval arrives
    return state


def resume_after_human_approval(investigation_id: str, approved: bool, officer_id: str):
    """Called by dashboard when officer makes decision"""
    state = load_state(investigation_id)
    state.human_approval_status = "APPROVED" if approved else "DECLINED"
    state.investigation_status = "IN_PROGRESS"
    save_state(state)
    
    # Record audit event
    record_audit_event(investigation_id, "HUMAN_APPROVAL", {
        "officer_id": officer_id,
        "decision": "APPROVED" if approved else "DECLINED"
    })
    
    # Resume investigation
    continue_investigation(state)
```

---

## 17. Error Handling

```python
class ToolExecutionError(Exception):
    pass

class ScopeLimitError(Exception):
    pass

class ToolNotPermittedError(Exception):
    pass


def call_tool_safely(
    tool_name: str,
    tool_args: dict,
    state: InvestigationState
) -> ToolResult:
    """Execute a tool call with error handling"""

    try:
        # Guardrail check
        guardrail = ToolGuardrail()
        guardrail.check(tool_name, tool_args, state)

        # Execute tool
        tool_func = get_tool_function(tool_name)
        raw_result = tool_func(**tool_args)

        # Log to audit
        record_audit_event(state.investigation_id, "TOOL_CALLED", {
            "tool_name": tool_name,
            "input_hash": hash_dict(tool_args),
            "output_hash": hash_dict(raw_result)
        })

        return ToolResult(
            tool_name=tool_name,
            success=True,
            data=raw_result,
            error=None,
            execution_time_ms=measure_time()
        )

    except ScopeLimitError as e:
        # This is expected — signal to stop investigation
        return ToolResult(tool_name=tool_name, success=False, 
                         data=None, error=f"SCOPE_LIMIT: {str(e)}", 
                         execution_time_ms=0)

    except ToolNotPermittedError as e:
        # Security violation — log and skip
        log_security_event(f"Attempted to call restricted tool: {tool_name}")
        return ToolResult(tool_name=tool_name, success=False,
                         data=None, error=f"NOT_PERMITTED: {str(e)}",
                         execution_time_ms=0)

    except Exception as e:
        # General failure — will be retried
        raise ToolExecutionError(f"Tool {tool_name} failed: {str(e)}") from e
```

---

## 18. Retry Logic

```python
import time

def call_tool_with_retry(
    tool_name: str,
    tool_args: dict,
    state: InvestigationState,
    max_retries: int = 3
) -> ToolResult:
    """Call a tool with exponential backoff retry"""

    for attempt in range(max_retries + 1):
        try:
            return call_tool_safely(tool_name, tool_args, state)

        except ToolExecutionError as e:
            if attempt == max_retries:
                # Final failure — log and return failure result
                log_warning(f"Tool {tool_name} permanently failed after {max_retries} retries")
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    data=None,
                    error=f"PERMANENT_FAILURE after {max_retries} retries: {str(e)}",
                    execution_time_ms=0
                )

            # Exponential backoff: 1s, 2s, 4s
            wait_seconds = 2 ** attempt
            log_info(f"Tool {tool_name} failed (attempt {attempt+1}), retrying in {wait_seconds}s")
            time.sleep(wait_seconds)
```

---

## 19. Observability

Every agent action should be traceable:

```python
import logging
import structlog

logger = structlog.get_logger()

def log_tool_call(investigation_id: str, tool_name: str, args: dict, result: ToolResult):
    logger.info(
        "tool_called",
        investigation_id=investigation_id,
        tool_name=tool_name,
        args_hash=hash_dict(args),
        success=result.success,
        execution_time_ms=result.execution_time_ms
    )

def log_state_snapshot(state: InvestigationState):
    logger.info(
        "state_snapshot",
        investigation_id=state.investigation_id,
        tool_calls_made=state.tool_calls_made,
        accounts_investigated=len(state.accounts_investigated),
        graph_depth=state.graph_depth_reached,
        flags=state.flags_raised,
        risk_score=state.fused_risk_score
    )
```

LangSmith or similar tracing tools can capture every LLM call, token usage, latency, and tool output for post-mortem analysis.

---

## 20. Evaluation

### Agent-level evaluation

```python
def evaluate_investigation(state: InvestigationState, ground_truth: dict) -> dict:
    """Evaluate a completed investigation"""
    
    # Did the agent predict the correct ATM?
    predicted_atm = state.withdrawal_prediction["top_atm"]["atm_id"]
    actual_atm = ground_truth["actual_withdrawal_atm"]
    top1_correct = (predicted_atm == actual_atm)
    
    # Was the correct ATM in top 3?
    top3_atms = [p["atm_id"] for p in state.withdrawal_prediction["top3"]]
    top3_correct = (actual_atm in top3_atms)
    
    # Lead time
    alert_time = state.alert_created_at
    withdrawal_time = ground_truth["actual_withdrawal_time"]
    lead_time_minutes = (withdrawal_time - alert_time).total_seconds() / 60
    
    return {
        "investigation_id": state.investigation_id,
        "top1_accuracy": int(top1_correct),
        "top3_accuracy": int(top3_correct),
        "lead_time_minutes": lead_time_minutes,
        "tool_calls_used": state.tool_calls_made,
        "false_positive": not ground_truth["withdrawal_occurred"],
        "investigation_time_minutes": (state.completed_at - state.started_at).total_seconds() / 60
    }
```

---

## 21. Tool Implementations

Each tool is a **typed, validated, controlled API function** that the agent can call. Here are implementations for all 14 tools:

---

### `get_complaint()`

**Purpose:** Retrieve structured complaint data by ID.

**Input schema:**
```python
class GetComplaintInput(BaseModel):
    complaint_id: str
```

**Output schema:**
```python
class ComplaintData(BaseModel):
    complaint_id: str
    complaint_no: str
    reported_at: datetime
    victim_account_id: str
    fraud_amount: float
    complaint_type: str
    district: str
    pincode: str
    status: str
```

**Implementation:**
```python
def get_complaint(complaint_id: str) -> ComplaintData:
    """Retrieve complaint from database"""
    # Validates complaint_id format
    if not complaint_id.startswith("CMP-"):
        raise ValueError("Invalid complaint ID format")
    
    row = db.query(
        "SELECT * FROM complaints WHERE id = %s", [complaint_id]
    )
    if not row:
        raise DataNotFoundError(f"Complaint {complaint_id} not found")
    
    return ComplaintData(**row)
```

**How agent uses it:**
```
State before: complaint_id known, no complaint data
Agent decision: call get_complaint(complaint_id)
State after: complaint data added to state.complaint
```

---

### `get_account()`

**Purpose:** Retrieve account profile by account ID.

**Input schema:**
```python
class GetAccountInput(BaseModel):
    account_id: str
```

**Output schema:**
```python
class AccountData(BaseModel):
    account_id: str
    bank: str
    account_type: str  # "savings", "current", "wallets"
    opened_at: datetime
    kyc_score: float   # 0-100
    is_mule_suspect: bool
    last_activity: datetime
```

**Implementation:**
```python
def get_account(account_id: str) -> AccountData:
    row = db.query("SELECT * FROM accounts WHERE id = %s", [account_id])
    if not row:
        raise DataNotFoundError(f"Account {account_id} not found")
    return AccountData(**row)
```

---

### `get_transactions()`

**Purpose:** Retrieve transaction history for an account.

**Input schema:**
```python
class GetTransactionsInput(BaseModel):
    account_id: str
    direction: Literal["incoming", "outgoing", "all"] = "all"
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    limit: int = 50
    min_amount: float = 0
```

**Output schema:**
```python
class TransactionList(BaseModel):
    account_id: str
    transactions: list[dict]
    total_count: int
    flags: list[str]  # e.g. ["STRUCTURING", "ROUND_AMOUNT"]
```

**Implementation:**
```python
def get_transactions(
    account_id: str,
    direction: str = "all",
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = 50,
    min_amount: float = 0
) -> TransactionList:
    
    # Build query safely (no raw string interpolation)
    query = """
        SELECT * FROM transactions 
        WHERE (from_account = %s OR to_account = %s)
        AND amount >= %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    rows = db.query(query, [account_id, account_id, min_amount, limit])
    
    # Apply automatic flag detection
    flags = detect_transaction_flags(rows)
    
    return TransactionList(
        account_id=account_id,
        transactions=rows,
        total_count=len(rows),
        flags=flags
    )
```

---

### `get_related_accounts()`

**Purpose:** Find accounts linked to the target account (shared phone, device, address).

**Input schema:**
```python
class GetRelatedAccountsInput(BaseModel):
    account_id: str
    relationship_types: list[str] = ["phone", "device", "address", "nominee"]
```

**Output schema:**
```python
class RelatedAccounts(BaseModel):
    account_id: str
    related: list[dict]  # {account_id, relationship_type, strength}
```

---

### `trace_transaction_graph()`

**Purpose:** Traverse the multi-hop transaction graph from a starting account.

**Input schema:**
```python
class TraceTransactionGraphInput(BaseModel):
    start_account_id: str
    max_depth: int = 5           # Enforced hard limit
    max_accounts: int = 50       # Enforced hard limit
    direction: str = "outgoing"
    time_window_hours: int = 24
    min_amount: float = 1000
```

**Output schema:**
```python
class TransactionGraph(BaseModel):
    nodes: list[dict]            # {id, type, risk_score}
    edges: list[dict]            # {from, to, amount, timestamp}
    suspicious_paths: list[dict] # paths with flags
    depth_reached: int
    accounts_explored: int
```

**Implementation:**
```python
def trace_transaction_graph(
    start_account_id: str,
    max_depth: int = 5,
    max_accounts: int = 50,
    direction: str = "outgoing",
    time_window_hours: int = 24,
    min_amount: float = 1000
) -> TransactionGraph:
    """Multi-hop graph traversal via Neo4j"""
    
    # Enforce maximum limits regardless of input
    max_depth = min(max_depth, 5)
    max_accounts = min(max_accounts, 50)
    
    cypher_query = """
    MATCH path = (start:Account {id: $account_id})-[:TRANSFERRED_TO*1..{depth}]->(end:Account)
    WHERE all(r IN relationships(path) WHERE r.amount >= $min_amount)
    RETURN nodes(path), relationships(path)
    LIMIT $limit
    """.format(depth=max_depth)
    
    result = neo4j_driver.run(cypher_query, {
        "account_id": start_account_id,
        "min_amount": min_amount,
        "limit": max_accounts * 10
    })
    
    # Parse and detect suspicious patterns
    nodes, edges = parse_graph_result(result)
    suspicious_paths = detect_suspicious_patterns(nodes, edges)
    
    return TransactionGraph(
        nodes=nodes,
        edges=edges,
        suspicious_paths=suspicious_paths,
        depth_reached=calculate_max_depth(edges),
        accounts_explored=len(set(e["from"] for e in edges) | set(e["to"] for e in edges))
    )
```

---

### `calculate_account_risk()`

**Purpose:** Call the ML AccountRiskScorer to compute a numerical risk score.

**Input schema:**
```python
class CalculateAccountRiskInput(BaseModel):
    account_id: str
    features: dict  # Feature dict prepared by feature engineering
```

**Output schema:**
```python
class AccountRiskResult(BaseModel):
    account_id: str
    risk_score: float        # 0-100 (from ML model, NOT LLM)
    risk_level: str          # LOW / MEDIUM / HIGH / CRITICAL
    model_version: str
    feature_importance: dict  # SHAP values
```

**Implementation:**
```python
def calculate_account_risk(account_id: str, features: dict) -> AccountRiskResult:
    """Call ML service for account risk scoring"""
    
    # Feature engineering (deterministic — not LLM)
    engineered_features = feature_engineer_account(account_id, features)
    
    # Call ML service (NOT LLM)
    response = requests.post(
        "http://ml-service/api/account-risk",
        json={"account_id": account_id, "features": engineered_features}
    )
    response.raise_for_status()
    data = response.json()
    
    # The ML model produced this score — the LLM did not
    return AccountRiskResult(
        account_id=account_id,
        risk_score=data["risk_score"],    # e.g. 84.2
        risk_level=data["risk_level"],    # e.g. "HIGH"
        model_version=data["model_version"],
        feature_importance=data["shap_values"]
    )
```

---

### `detect_transaction_anomaly()`

**Purpose:** Run Isolation Forest anomaly detection on transaction pattern.

**Input schema:**
```python
class DetectTransactionAnomalyInput(BaseModel):
    transaction_ids: list[str]
    account_id: str
```

**Output schema:**
```python
class AnomalyResult(BaseModel):
    account_id: str
    anomaly_score: float     # -1 to 1 (negative = more anomalous)
    is_anomalous: bool
    anomalous_features: list[str]
```

---

### `get_withdrawal_history()`

**Purpose:** Get historical ATM withdrawal records for an account.

**Input schema:**
```python
class GetWithdrawalHistoryInput(BaseModel):
    account_id: str
    lookback_days: int = 90
    limit: int = 100
```

**Output schema:**
```python
class WithdrawalHistory(BaseModel):
    account_id: str
    withdrawals: list[dict]  # {atm_id, amount, timestamp, lat, lon}
    preferred_atm_clusters: list[dict]  # Geographic clusters
    total_withdrawn: float
```

---

### `get_atm_locations()`

**Purpose:** Get ATM location data near a set of coordinates or for specific ATM IDs.

**Input schema:**
```python
class GetATMLocationsInput(BaseModel):
    atm_ids: Optional[list[str]] = None   # Specific ATMs
    center_lat: Optional[float] = None    # OR search by location
    center_lon: Optional[float] = None
    radius_km: float = 5.0
    limit: int = 20
```

**Output schema:**
```python
class ATMLocationResult(BaseModel):
    atms: list[dict]  # {atm_id, lat, lon, bank, district, fraud_history_score}
```

---

### `get_geographic_risk()`

**Purpose:** Get geographic risk score for a location from the Geospatial Engine.

**Input schema:**
```python
class GetGeographicRiskInput(BaseModel):
    lat: float
    lon: float
    radius_km: float = 3.0
    time_of_day: Optional[int] = None  # Hour 0-23
```

**Output schema:**
```python
class GeographicRiskResult(BaseModel):
    location: dict   # {lat, lon}
    risk_score: float  # 0-100
    hotspot_rank: int  # Rank among all clusters nationally
    nearby_complaint_count: int
    crime_density_score: float
```

---

### `predict_withdrawal_location()`

**Purpose:** Call the ML WithdrawalLocationPredictor to get top-K predicted ATMs.

**Input schema:**
```python
class PredictWithdrawalLocationInput(BaseModel):
    account_ids: list[str]      # Suspect accounts
    investigation_id: str
    features: dict              # Combined ML features
```

**Output schema:**
```python
class WithdrawalPrediction(BaseModel):
    investigation_id: str
    predictions: list[dict]     # [{atm_id, probability, lat, lon, district}]
    predicted_window_start: datetime
    predicted_window_end: datetime
    model_version: str
    confidence: float
```

**Implementation:**
```python
def predict_withdrawal_location(
    account_ids: list[str],
    investigation_id: str,
    features: dict
) -> WithdrawalPrediction:
    """Call ML service for withdrawal location prediction — NOT LLM"""
    
    # Build feature vector from account history and geographic data
    ml_features = build_withdrawal_prediction_features(account_ids, features)
    
    # Call ML service (Gradient Boosting + KDE model)
    response = requests.post(
        "http://ml-service/api/withdrawal-location",
        json={
            "account_ids": account_ids,
            "features": ml_features,
            "top_k": 5
        }
    )
    response.raise_for_status()
    data = response.json()
    
    return WithdrawalPrediction(
        investigation_id=investigation_id,
        predictions=data["predictions"],
        predicted_window_start=parse_datetime(data["window_start"]),
        predicted_window_end=parse_datetime(data["window_end"]),
        model_version=data["model_version"],
        confidence=data["confidence"]
    )
```

---

### `get_nearby_complaints()`

**Purpose:** Find other cybercrime complaints in the same geographic area.

**Input schema:**
```python
class GetNearbyComplaintsInput(BaseModel):
    lat: float
    lon: float
    radius_km: float = 10.0
    since_days: int = 30
    limit: int = 20
```

**Output schema:**
```python
class NearbyComplaintsResult(BaseModel):
    complaints: list[dict]
    total_count: int
    dominant_complaint_type: str
```

---

### `create_alert()`

**Purpose:** Generate an official alert and dispatch to LEA/bank/I4C.

**Input schema:**
```python
class CreateAlertInput(BaseModel):
    investigation_id: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "EXTREME"]
    risk_score: float
    withdrawal_prediction: dict
    evidence_summary: str
    human_approved: bool
    approver_id: Optional[str]
```

**Output schema:**
```python
class AlertResult(BaseModel):
    alert_id: str
    dispatched_to: list[str]
    created_at: datetime
```

---

### `generate_report()`

**Purpose:** Generate a human-readable intelligence report summarizing the investigation.

**Input schema:**
```python
class GenerateReportInput(BaseModel):
    investigation_id: str
    state: dict  # Full InvestigationState dict
```

**Output schema:**
```python
class IntelligenceReport(BaseModel):
    report_id: str
    summary: str           # 1-paragraph summary
    evidence_chain: list[str]  # Numbered evidence points
    risk_assessment: str   # Risk level explanation
    predicted_locations: list[dict]
    recommended_action: str
    confidence_note: str   # Always includes uncertainty disclaimer
    generated_at: datetime
```

**This is where the LLM IS used — for writing human-readable text from structured data:**
```python
def generate_report(investigation_id: str, state: dict) -> IntelligenceReport:
    """LLM generates human-readable report FROM structured data"""
    
    # Structured data is passed to LLM — LLM writes text, not numbers
    prompt = f"""
    Write a concise intelligence report for investigators.
    
    Investigation ID: {investigation_id}
    Evidence gathered:
    {json.dumps(state['evidence_summary'], indent=2)}
    
    Risk score (calculated by ML): {state['fused_risk_score']}
    Predicted ATMs: {json.dumps(state['withdrawal_prediction']['predictions'][:3], indent=2)}
    
    Rules:
    - Do not invent facts not in the evidence
    - Always include: "This is a probabilistic prediction, not a certainty"
    - Write for a law enforcement audience
    - Keep under 500 words
    """
    
    report_text = llm.generate(prompt)
    return IntelligenceReport(...)
```

---

### `record_audit_event()`

**Purpose:** Record a tamper-evident audit event in the blockchain-style hash chain.

**Input schema:**
```python
class RecordAuditEventInput(BaseModel):
    investigation_id: str
    event_type: str
    event_data: dict        # Will be hashed — no raw PII
    previous_hash: str
```

**Output schema:**
```python
class AuditEventResult(BaseModel):
    event_id: str
    event_hash: str    # SHA-256 of (event_data + previous_hash)
    chain_hash: str    # New chain head
    timestamp: datetime
```

---

## 22. Minimal Conceptual Agent

Here is the simplest possible agent that demonstrates the full loop:

```python
"""
Minimal PCCWIS investigation agent (conceptual).
Not production code — simplified for learning.
"""

from pydantic import BaseModel
from typing import Optional
import json

# --- State ---
class MinimalInvestigationState(BaseModel):
    investigation_id: str
    complaint_id: str
    complaint: Optional[dict] = None
    victim_account: Optional[dict] = None
    suspect_accounts: list[dict] = []
    transactions: list[dict] = []
    risk_scores: dict[str, float] = {}
    withdrawal_prediction: Optional[dict] = None
    fused_risk_score: Optional[float] = None
    tool_calls: int = 0
    max_tool_calls: int = 20  # Very small for learning example


# --- Tools (simplified) ---
def get_complaint(complaint_id: str) -> dict:
    return {"id": complaint_id, "victim_account_id": "V001", "amount": 80000}

def get_account(account_id: str) -> dict:
    # In real system: database query
    return {"id": account_id, "bank": "SBI", "kyc_score": 45}

def get_transactions(account_id: str) -> dict:
    # In real system: database query
    return {
        "transactions": [
            {"to": "M001", "amount": 80000, "timestamp": "2024-01-15T12:16:00"}
        ]
    }

def calculate_account_risk(account_id: str) -> dict:
    # In real system: call ML service
    return {"account_id": account_id, "risk_score": 84.2, "risk_level": "HIGH"}

def predict_withdrawal_location(account_ids: list) -> dict:
    # In real system: call ML service
    return {
        "predictions": [{"atm_id": "ATM-001", "probability": 0.67}],
        "confidence": 0.82
    }


# --- Tool Registry ---
TOOLS = {
    "get_complaint": get_complaint,
    "get_account": get_account,
    "get_transactions": get_transactions,
    "calculate_account_risk": calculate_account_risk,
    "predict_withdrawal_location": predict_withdrawal_location,
}


# --- Simple Agent Loop ---
def run_minimal_investigation(complaint_id: str) -> MinimalInvestigationState:
    state = MinimalInvestigationState(
        investigation_id="INV-001",
        complaint_id=complaint_id
    )
    
    # Step 1: Get complaint
    state.complaint = TOOLS["get_complaint"](complaint_id)
    state.tool_calls += 1
    
    # Step 2: Get victim account
    victim_id = state.complaint["victim_account_id"]
    state.victim_account = TOOLS["get_account"](victim_id)
    state.tool_calls += 1
    
    # Step 3: Get transactions
    txn_result = TOOLS["get_transactions"](victim_id)
    state.transactions = txn_result["transactions"]
    state.tool_calls += 1
    
    # Step 4: For each destination account, get risk
    suspect_account_ids = [t["to"] for t in state.transactions]
    for acc_id in suspect_account_ids:
        if state.tool_calls >= state.max_tool_calls:
            break  # Scope limit
        risk = TOOLS["calculate_account_risk"](acc_id)
        state.risk_scores[acc_id] = risk["risk_score"]
        state.tool_calls += 1
    
    # Step 5: Predict withdrawal location (ML, not LLM)
    state.withdrawal_prediction = TOOLS["predict_withdrawal_location"](suspect_account_ids)
    state.tool_calls += 1
    
    # Step 6: Simple risk fusion (in real system: Risk Fusion Engine)
    avg_risk = sum(state.risk_scores.values()) / max(len(state.risk_scores), 1)
    state.fused_risk_score = avg_risk * 0.6 + state.withdrawal_prediction["confidence"] * 40
    
    return state


# Run it
result = run_minimal_investigation("CMP-987654")
print(f"Investigation complete. Risk score: {result.fused_risk_score:.1f}")
print(f"Predicted ATM: {result.withdrawal_prediction['predictions'][0]['atm_id']}")
print(f"Tool calls used: {result.tool_calls}")
```

This minimal agent:
- Has no LLM (fully hardcoded sequence)
- Demonstrates state accumulation
- Shows scope limit enforcement
- Shows that ML provides the numbers (not hardcoded)

---

## 23. Evolution to LangGraph

The minimal agent above has a **fixed sequence**. Real investigations require **dynamic decision-making**.

LangGraph adds:

| Feature | Minimal Agent | LangGraph Agent |
|---|---|---|
| **Control flow** | Fixed sequence | Dynamic conditional edges |
| **State** | Python object | TypedDict / Pydantic + checkpointing |
| **LLM decisions** | None | LLM decides next node |
| **Human-in-the-loop** | Not supported | `interrupt()` on any node |
| **Parallelism** | Sequential only | Parallel tool calls |
| **Persistence** | Redis manually | Built-in checkpointer |
| **Retries** | Manual | Built-in retry policies |
| **Observability** | Manual logging | LangSmith tracing |

**LangGraph equivalent of our minimal agent:**

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# See langgraph_architecture_over.md for complete implementation

def build_investigation_graph():
    graph = StateGraph(InvestigationState)
    
    # Add nodes (each node is a function that modifies state)
    graph.add_node("ingest_complaint", ingest_complaint_node)
    graph.add_node("fetch_account", fetch_account_node)
    graph.add_node("trace_transactions", trace_transactions_node)
    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("predict_withdrawal", predict_withdrawal_node)
    graph.add_node("risk_fusion", risk_fusion_node)
    graph.add_node("decision", decision_node)
    graph.add_node("generate_alert", generate_alert_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("audit", audit_node)
    
    # Add edges
    graph.set_entry_point("ingest_complaint")
    graph.add_edge("ingest_complaint", "fetch_account")
    graph.add_edge("fetch_account", "trace_transactions")
    graph.add_edge("trace_transactions", "assess_risk")
    graph.add_edge("assess_risk", "predict_withdrawal")
    graph.add_edge("predict_withdrawal", "risk_fusion")
    
    # Conditional edges from decision node
    graph.add_conditional_edges(
        "decision",
        route_by_risk_level,  # Function that reads state and returns next node name
        {
            "generate_alert": "generate_alert",
            "generate_report": "generate_report",
            "monitor": END
        }
    )
    
    graph.add_edge("generate_alert", "audit")
    graph.add_edge("generate_report", "audit")
    graph.add_edge("audit", END)
    
    # Add checkpointing for persistence and human-in-the-loop
    return graph.compile(checkpointer=MemorySaver())
```

See [`langgraph_architecture_over.md`](./langgraph_architecture_over.md) for the complete LangGraph implementation guide.

---

*Document version: 1.0 | PCCWIS — Problem Statement ID 26184*
