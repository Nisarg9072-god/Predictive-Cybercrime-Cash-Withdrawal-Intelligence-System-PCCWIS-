"""
llm/prompts.py — Structured prompt templates for cybercrime investigation.

RULES enforced in every prompt:
  - Only supplied evidence may be referenced.
  - Never invent transactions, accounts, banks, or victims.
  - Clearly distinguish OBSERVED / DERIVED / INFERRED / PREDICTED.
  - Never modify numerical risk scores.
  - If evidence is insufficient, say so explicitly.
"""

from typing import Any, Dict, List


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_INVESTIGATOR = """You are a senior cybercrime intelligence analyst working on cash-withdrawal fraud investigations in India.

STRICT RULES — violation is unacceptable:
1. Use ONLY the evidence supplied in the CONTEXT block. Never invent facts.
2. Clearly label each statement as OBSERVED, DERIVED, or INFERRED.
3. OBSERVED = directly from a database record. DERIVED = calculated from observed data. INFERRED = reasoned from patterns.
4. Never change, override, or contradict numerical risk scores provided to you.
5. Never fabricate account IDs, transaction IDs, bank names, or victim details.
6. If evidence is insufficient for a conclusion, state: "Insufficient evidence to conclude X."
7. Write concise, professional intelligence analyst language. No speculation beyond the evidence.
"""


# ── Hypothesis generation ─────────────────────────────────────────────────────

def build_hypothesis_prompt(state: Dict[str, Any]) -> str:
    accounts = state.get("accounts", [])
    transactions = state.get("transactions", [])
    profiles = state.get("profiles", [])
    scenario_id = state.get("scenario_id", "UNKNOWN")
    existing_hyp = [h.get("description", "") for h in state.get("hypotheses", [])]

    txn_summary = ""
    if transactions:
        txn_summary = f"  - {len(transactions)} transactions found\n"
        total = sum(t.get("amount_inr", 0) for t in transactions if isinstance(t, dict))
        laundering = sum(1 for t in transactions if isinstance(t, dict) and t.get("is_laundering"))
        txn_summary += f"  - Total amount: ₹{total:,.0f}\n"
        txn_summary += f"  - Flagged as laundering: {laundering}/{len(transactions)}\n"

    profile_summary = ""
    if profiles:
        mules = [p for p in profiles if isinstance(p, dict) and p.get("is_mule")]
        profile_summary = f"  - {len(profiles)} profiles analysed, {len(mules)} mule accounts\n"

    existing_str = "\n".join(f"  - {h}" for h in existing_hyp) if existing_hyp else "  None yet."

    return f"""CONTEXT — Investigation State for {scenario_id}:

Identified accounts: {accounts}
{txn_summary}{profile_summary}
Existing hypotheses:
{existing_str}

TASK:
Generate ONE new investigative hypothesis that is NOT already listed above and is directly supported by the evidence above.
Respond with JSON:
{{
  "description": "...",
  "category": "LAUNDERING|CASHOUT|MULE_NETWORK|IDENTITY_FRAUD|GEOGRAPHIC_CONCENTRATION",
  "confidence": 0.0-1.0,
  "reasoning": "Cite specific evidence from CONTEXT only."
}}"""


# ── Action ranking ─────────────────────────────────────────────────────────────

def build_action_ranking_prompt(
    state: Dict[str, Any],
    available_tools: List[str],
    completed_tools: List[str],
) -> str:
    accounts = state.get("accounts", [])[:5]
    transactions = len(state.get("transactions", []))
    chains = len(state.get("transaction_chains", []))
    profiles = len(state.get("profiles", []))
    atms = len(state.get("atms", []))
    findings = len(state.get("findings", []))

    return f"""CONTEXT — Current investigation state:
  Accounts identified: {accounts}
  Transactions found: {transactions}
  Chains traced: {chains}
  Profiles analysed: {profiles}
  ATMs investigated: {atms}
  Findings generated: {findings}

Available tools (not yet called):
{chr(10).join(f"  - {t}" for t in available_tools if t not in completed_tools)}

TASK:
Select the SINGLE most valuable next investigative action from the available tools above.
Respond with JSON:
{{
  "tool": "<tool_name>",
  "reason": "Brief justification based only on current state gaps."
}}
If no useful action remains, respond with: {{"tool": "STOP", "reason": "..."}}"""


# ── Finding explanation ───────────────────────────────────────────────────────

def build_finding_explanation_prompt(finding: Dict[str, Any], evidence: List[Dict[str, Any]]) -> str:
    ev_lines = []
    for e in evidence[:10]:
        ev_lines.append(
            f"  [{e.get('classification','?')}] {e.get('observed_field','')}: "
            f"{e.get('observed_value','')} (confidence={e.get('confidence',0):.2f})"
        )
    ev_str = "\n".join(ev_lines) if ev_lines else "  No evidence supplied."

    return f"""CONTEXT — Finding:
  Title: {finding.get('title', '')}
  Category: {finding.get('category', '')}
  Severity: {finding.get('severity', '')}
  Confidence: {finding.get('confidence', 0):.2f}
  Description: {finding.get('description', '')}

Supporting evidence ({len(evidence)} items):
{ev_str}

TASK:
Write a clear, professional 3-5 sentence explanation of this finding for an intelligence report.
Reference only the evidence above. Use OBSERVED/DERIVED/INFERRED labels.
Do NOT change the severity or confidence values.
Respond with plain text (no JSON)."""


# ── Executive summary ─────────────────────────────────────────────────────────

def build_executive_summary_prompt(
    scenario: Dict[str, Any],
    findings: List[Dict[str, Any]],
    risk: Dict[str, Any],
    money_flow: List[Dict[str, Any]],
) -> str:
    finding_bullets = "\n".join(
        f"  - [{f.get('severity','')}] {f.get('title','')}: {f.get('description','')[:120]}..."
        for f in findings[:5]
    )
    chain_count = len(money_flow)
    total_hops = sum(t.get("hop_layer", 0) for t in money_flow if isinstance(t, dict))

    return f"""CONTEXT — Investigation Summary:
  Case: {scenario.get('scenario_id', '')} — {scenario.get('scenario_name', '')}
  Crime category: {scenario.get('crime_category', '')}
  Victim city/state: {scenario.get('victim_city', '')} / {scenario.get('victim_state', '')}
  Amount lost: ₹{scenario.get('amount_lost_inr', 0):,.0f}
  Risk score: {risk.get('risk_score', 0):.1f}/100 ({risk.get('risk_level', 'UNKNOWN')})
  Transaction chains: {chain_count}, total hop layers traced: {total_hops}
  Findings:
{finding_bullets if finding_bullets else "  None generated."}

TASK:
Write a professional executive summary (150-200 words) suitable for a senior law enforcement officer.
Describe: what happened, how the money moved, what the key risks are, and what immediate action is recommended.
Reference only the evidence above. Begin with the case context. End with the recommended action.
Respond with plain text."""
