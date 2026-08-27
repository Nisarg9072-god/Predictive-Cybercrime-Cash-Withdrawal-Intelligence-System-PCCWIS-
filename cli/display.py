"""
cli/display.py — Terminal display formatters for investigation output.

All display functions write only to stdout. 
PII sanitization is applied before calling these functions by the caller.
"""

from typing import Any, Dict, List, Optional


DIVIDER = "-" * 60
HEADER  = "=" * 60


def _bold(text: str) -> str:
    """ANSI bold — degrades gracefully in terminals without ANSI support."""
    return f"\033[1m{text}\033[0m"


def display_case_summary(scenario: Dict[str, Any]) -> None:
    print(f"\n{DIVIDER}")
    print(_bold("  CASE SUMMARY"))
    print(DIVIDER)
    print(f"  Case ID       : {scenario.get('scenario_id', 'N/A')}")
    print(f"  Case Name     : {scenario.get('scenario_name', 'N/A')}")
    print(f"  Crime Category: {scenario.get('crime_category', 'N/A')}")
    print(f"  Victim City   : {scenario.get('victim_city', 'N/A')}")
    print(f"  Victim State  : {scenario.get('victim_state', 'N/A')}")
    print(f"  Amount Lost   : ₹{scenario.get('amount_lost_inr', 0):,.0f}")
    print(f"  Status        : {scenario.get('status', 'N/A')}")
    print(DIVIDER)


def display_progress(step: int, total: int, label: str) -> None:
    bar_width = 30
    filled = int(bar_width * step / total)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"\r  [{step:2d}/{total}] {bar} {label}", end="\n", flush=True)


def display_money_flow(transactions: List[Dict[str, Any]], chains: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Renders a hop-by-hop ASCII money flow diagram from transaction data.
    Only uses actual database evidence — never invents transfers.
    """
    print(f"\n{HEADER}")
    print(_bold("  MONEY FLOW"))
    print(HEADER)

    if not transactions:
        print("  [NO TRANSACTIONS] Insufficient transaction data to display money flow.")
        print(HEADER)
        return

    # Group by chain_id
    chain_groups: Dict[str, List[Dict[str, Any]]] = {}
    unchained = []
    for txn in transactions:
        if isinstance(txn, dict):
            cid = txn.get("chain_id") or txn.get("txn_id", "UNKNOWN")
            chain_groups.setdefault(cid, []).append(txn)
        elif hasattr(txn, "__dict__"):
            d = txn.__dict__ if not hasattr(txn, "model_dump") else txn.model_dump()
            cid = d.get("chain_id") or d.get("txn_id", "UNKNOWN")
            chain_groups.setdefault(cid, []).append(d)

    for chain_id, txns in list(chain_groups.items())[:3]:  # Show up to 3 chains
        # Sort by hop_layer
        txns_sorted = sorted(txns, key=lambda t: t.get("hop_layer", 0))
        print(f"\n  CHAIN: {chain_id}")
        print(f"  {'─' * 50}")

        prev_to = None
        for i, txn in enumerate(txns_sorted):
            frm = txn.get("from_account_id", "???")
            to  = txn.get("to_account_id",   "???")
            amt = txn.get("amount_inr", 0)
            bank_frm = txn.get("from_bank", "")
            bank_to  = txn.get("to_bank", "")
            ts   = txn.get("timestamp_ist", "")
            hop  = txn.get("hop_layer", i)
            flag = "⚠ LAUNDERING" if txn.get("is_laundering") else ""
            term = "⚑ TERMINAL CASHOUT" if txn.get("is_terminal_cashout") else ""

            if i == 0:
                print(f"  Hop {hop:2d} | FROM: {_mask_account(frm)} [{bank_frm}]")
            print(f"         |   ↓  ₹{amt:>12,.0f}  {flag} {term}")
            print(f"         |    {ts}")
            print(f"  Hop {hop+1:2d} |   TO: {_mask_account(to)} [{bank_to}]")

        print(f"  {'─' * 50}")
        total = sum(t.get("amount_inr", 0) for t in txns_sorted)
        laundering = sum(1 for t in txns_sorted if t.get("is_laundering"))
        cashout = sum(1 for t in txns_sorted if t.get("is_terminal_cashout"))
        print(f"  Chain total: ₹{total:,.0f}  |  Hops: {len(txns_sorted)}  "
              f"|  Flagged: {laundering}  |  Cashouts: {cashout}")

    if len(chain_groups) > 3:
        print(f"\n  ... and {len(chain_groups) - 3} more chains (see PDF report)")

    print(HEADER)


def display_risk_assessment(risk: Dict[str, Any]) -> None:
    print(f"\n{HEADER}")
    print(_bold("  RISK ASSESSMENT"))
    print(HEADER)
    score = risk.get("risk_score", 0)
    level = risk.get("risk_level", "UNKNOWN")
    conf  = risk.get("confidence", 0)
    bar   = _risk_bar(score)
    print(f"  Risk Score : {score:.1f}/100  {bar}")
    print(f"  Risk Level : {level}")
    print(f"  Confidence : {conf:.0%}")
    indicators = risk.get("indicators", [])
    if indicators:
        print(f"\n  Indicators ({len(indicators)}):")
        for ind in indicators[:8]:
            if isinstance(ind, dict):
                print(f"    ▸ {ind.get('indicator_id', ind.get('name', '?'))}")
    print(HEADER)


def display_findings(findings: List[Dict[str, Any]]) -> None:
    print(f"\n{HEADER}")
    print(_bold("  KEY FINDINGS"))
    print(HEADER)
    if not findings:
        print("  No findings generated.")
    for i, f in enumerate(findings, 1):
        if isinstance(f, dict):
            print(f"\n  Finding {i}: {f.get('title', 'Untitled')}")
            print(f"  Severity  : {f.get('severity', 'N/A')}")
            print(f"  Confidence: {f.get('confidence', 0):.0%}")
            print(f"  Category  : {f.get('category', 'N/A')}")
            desc = f.get("description", "")
            if desc:
                # Wrap at 70 chars
                words = desc.split()
                line = "  "
                for w in words:
                    if len(line) + len(w) > 72:
                        print(line)
                        line = "  " + w + " "
                    else:
                        line += w + " "
                if line.strip():
                    print(line)
            ev_ids = f.get("evidence_ids", [])
            if ev_ids:
                print(f"  Evidence  : {', '.join(ev_ids[:5])}")
            llm_exp = f.get("llm_explanation", "")
            if llm_exp:
                print(f"\n  [LLM] {llm_exp[:300]}")
    print(HEADER)


def display_report(pdf_path: str, sha256: str, report_id: str) -> None:
    print(f"\n{HEADER}")
    print(_bold("  REPORT GENERATED"))
    print(HEADER)
    print(f"  Report ID : {report_id}")
    print(f"  PDF Path  : {pdf_path}")
    print(f"  SHA-256   : {sha256}")
    print(HEADER)


def display_blocked(reason: str) -> None:
    print(f"\n{HEADER}")
    print(_bold("  ⛔  INVESTIGATION BLOCKED"))
    print(HEADER)
    print(f"  Reason: {reason}")
    print(HEADER)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_account(account_id: str) -> str:
    """Show only last 6 chars of account ID for display."""
    if len(account_id) > 10:
        return "****" + account_id[-6:]
    return account_id


def _risk_bar(score: float) -> str:
    filled = int(score / 5)
    empty  = 20 - filled
    color  = "🔴" if score >= 70 else "🟠" if score >= 40 else "🟢"
    return f"{color} [{'█' * filled}{'░' * empty}]"
