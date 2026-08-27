"""
cli/main.py — Predictive Cybercrime Cash Withdrawal Intelligence System CLI.

Primary entry point:
    python -m cli.main investigate

All investigation data comes exclusively from the master dataset at DATASET_DB_PATH.
No synthetic or mock data is used in the production 'investigate' command.
"""

import sys
import argparse
import os

# Force stdout to UTF-8 to prevent charmap errors on Windows with emojis
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agent.agent import PredictiveCybercrimeAgent
from database.connection import get_dataset_connection
from database.repository import DatasetRepository, OperationalRepository
from config import config
from reporting.service import ReportService
from reporting.models import ReportMode
from evaluation.engine import EvaluationEngine
from agent.tools import registry
from cli.display import (
    HEADER, DIVIDER,
    display_case_summary, display_progress, display_money_flow,
    display_risk_assessment, display_findings, display_report, display_blocked,
)
from risk.engine import RiskEngine
from llm.service import LLMService


# ── Interactive Investigation ─────────────────────────────────────────────────

def cmd_investigate_interactive(
    max_iterations: int = 15,
    max_tool_calls: int = 20,
) -> None:
    """
    Primary user-facing investigation command.
    Prompts for Case ID and victim, validates against master dataset,
    runs the LangGraph agent, displays money flow + risk, auto-generates PDF.
    """
    print(f"\n{HEADER}")
    print("  PREDICTIVE CYBERCRIME INTELLIGENCE SYSTEM")
    print("  Powered by LangGraph + Mistral + Deterministic Risk Engine")
    print(HEADER)

    llm_status = "ACTIVE" if LLMService.is_available() else "UNAVAILABLE (set MISTRAL_API_KEY)"
    print(f"\n  LLM Status : {llm_status}")
    print(f"  Dataset    : {config.DATASET_DB_PATH}")
    print()

    # ── Step 1: Case ID input ──────────────────────────────────────────────────
    print("  Enter Case / Scenario ID (e.g. SCENARIO_001):")
    scenario_id = input("  > ").strip().upper()
    if not scenario_id:
        print("\n  [ERROR] No Case ID entered. Exiting.")
        return

    # ── Step 2: Validate against DB ───────────────────────────────────────────
    print(f"\n  Validating case {scenario_id} against master dataset...")
    scenario = DatasetRepository.get_scenario(scenario_id)
    if not scenario:
        print(f"\n  CASE NOT FOUND: '{scenario_id}' does not exist in the master dataset.")
        print("  Available cases: SCENARIO_001, SCENARIO_002, SCENARIO_003, SCENARIO_004, SCENARIO_005")
        return

    scenario_dict = scenario.model_dump()
    display_case_summary(scenario_dict)

    # ── Step 3: Victim Name input ──────────────────────────────────────────────
    print("\n  Enter Victim Name (as reported):")
    victim_name = input("  > ").strip()
    if not victim_name:
        print("\n  [WARNING] No victim name entered. Continuing without victim validation.")

    print("\n  Enter Victim Account ID (optional, press Enter to skip):")
    victim_account_id = input("  > ").strip() or None

    # ── Step 4: Victim validation (loose — schema has no victim_name column) ──
    # We accept victim name as informational context on the report.
    # If an account ID is supplied, we confirm it appears in transactions.
    if victim_account_id:
        print(f"\n  Verifying account {victim_account_id[-6:]}... ", end="", flush=True)
        txns = DatasetRepository.search_transactions(from_account=victim_account_id, limit=3)
        if not txns:
            txns = DatasetRepository.search_transactions(to_account=victim_account_id, limit=3)
        if txns:
            print("FOUND in transaction records.")
        else:
            print("NOT FOUND in transaction records.")
            print("\n  VICTIM MISMATCH: The supplied account ID has no transaction records.")
            print("  Proceeding with investigation using scenario data only.")
            victim_account_id = None

    # ── Step 5: Confirmation ───────────────────────────────────────────────────
    print(f"\n  Victim       : {victim_name or '(not supplied)'}")
    print(f"  Account      : {('****' + victim_account_id[-6:]) if victim_account_id else '(not supplied)'}")
    print(f"  Max Steps    : {max_iterations} iterations, {max_tool_calls} tool calls")
    print(f"\n  Start investigation? [y/N] ", end="")
    confirm = input().strip().lower()
    if confirm not in ("y", "yes"):
        print("  Investigation cancelled.")
        return

    # ── Step 6: Run Investigation ──────────────────────────────────────────────
    print(f"\n{HEADER}")
    print("  INVESTIGATION STARTED")
    print(HEADER)

    agent = PredictiveCybercrimeAgent()
    final_state = None

    steps = [
        "Validating case",
        "Loading case context",
        "Identifying accounts",
        "Tracing transactions",
        "Building money-flow chain",
        "Analysing profiles",
        "Analysing cashout locations",
        "Calculating risk",
        "Reviewing evidence",
        "Generating report",
    ]
    total_steps = len(steps)

    # Show initial progress
    for i, label in enumerate(steps[:3], 1):
        display_progress(i, total_steps, label)

    try:
        final_state = agent.run(
            scenario_id=scenario_id,
            max_iterations=max_iterations,
            max_tool_calls=max_tool_calls,
            victim_name=victim_name,
            victim_account_id=victim_account_id,
        )
        for i, label in enumerate(steps[3:9], 4):
            display_progress(i, total_steps, label)

    except Exception as e:
        print(f"\n  [ERROR] Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    if not final_state:
        display_blocked("Agent returned no state — investigation could not complete.")
        return

    # ── Step 7: Display results ────────────────────────────────────────────────
    # Money Flow
    all_txns = final_state.get("transactions", []) + final_state.get("transaction_chains", [])
    display_money_flow(all_txns, final_state.get("transaction_chains"))

    # Risk
    analysis = RiskEngine.calculate_risk(final_state)
    display_risk_assessment(analysis)

    # Findings
    findings = final_state.get("findings", [])
    display_findings(findings)

    # ATM status
    if not final_state.get("atms"):
        print(f"\n  [BLOCKED] ATM Analysis: ATM table malformed in master dataset.")
        print("  ATM cashout location details are unavailable. See report for details.")

    # ── Step 8: Generate PDF Report ────────────────────────────────────────────
    display_progress(10, total_steps, "Generating report")
    svc = ReportService(output_dir="reports")
    try:
        # Generate LLM executive summary if available
        llm_summary = None
        if LLMService.is_available():
            ok, llm_summary = LLMService.generate_executive_summary(
                scenario_dict, findings, analysis,
                final_state.get("transactions", [])
            )
            if not ok:
                llm_summary = None

        # Augment state with executive summary for report builder
        final_state["llm_executive_summary"] = llm_summary
        final_state["victim_name"] = victim_name
        final_state["victim_account_id"] = victim_account_id

        res = svc.create_report(
            investigation_id=final_state.get("investigation_id", "UNKNOWN"),
            scenario_id=scenario_id,
            mode=ReportMode.REAL,
            agent_state=final_state,
            audit_events=[],
        )
        display_report(res["pdf_path"], res["sha256"], res["report_id"])
    except Exception as e:
        print(f"\n  [WARNING] Report generation failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n  Investigation completed.")
    print(HEADER)


# ── Legacy scenario-arg investigate (preserved for scripting) ─────────────────

def cmd_investigate(scenario_id: str, max_iterations: int = 15, max_tool_calls: int = 20, verbose: bool = False):
    print(HEADER)
    print("  Predictive Cybercrime Intelligence Agent CLI")
    print(HEADER)
    print(f"\n[INVESTIGATION STARTED]  Scenario: {scenario_id}\n")

    agent = PredictiveCybercrimeAgent()
    try:
        final_state = agent.run(scenario_id, max_iterations=max_iterations, max_tool_calls=max_tool_calls)

        if final_state:
            print(f"\n{HEADER}")
            print("CYBERCRIME INVESTIGATION RESULT\n")
            print(f"Scenario: {scenario_id}")
            print(f"Investigation ID: {final_state.get('investigation_id', 'unknown')}\n")

            all_txns = final_state.get("transactions", []) + final_state.get("transaction_chains", [])
            display_money_flow(all_txns, final_state.get("transaction_chains"))

            analysis = RiskEngine.calculate_risk(final_state)
            display_risk_assessment(analysis)
            display_findings(final_state.get("findings", []))

            print(f"\nStop Reason: {final_state.get('stop_reason', 'Unknown')}")
            print(HEADER)
    except Exception as e:
        print(f"\n[ERROR] Investigation failed: {e}")
        sys.exit(1)


# ── Report commands ──────────────────────────────────────────────────────────

def cmd_report_investigation(investigation_id: str, output_dir: str = "reports"):
    print(HEADER)
    print("  Report Generation")
    print(HEADER)
    print(f"Investigation ID: {investigation_id}")

    svc = ReportService(output_dir=output_dir)
    try:
        res = svc.create_report(
            investigation_id=investigation_id,
            scenario_id="UNKNOWN",
            mode=ReportMode.REAL,
            agent_state=None,
            audit_events=[],
        )
        print("\n[REPORT GENERATED SUCCESSFULLY]")
        print(f"Report ID : {res['report_id']}")
        print(f"PDF Path  : {res['pdf_path']}")
        print(f"SHA-256   : {res['sha256']}")
        print(f"Findings  : {res['findings_count']}")
    except Exception as e:
        print(f"\n[ERROR] Report generation failed: {e}")
        import traceback
        traceback.print_exc()


def cmd_report_verify(report_id: str):
    print(HEADER)
    print("  Report Verification")
    print(HEADER)
    svc = ReportService()
    res = svc.verify_report(report_id)
    print(f"\nStatus     : {res['status']}")
    if res.get("verified") is not None:
        print(f"Verified   : {res['verified']}")
        print(f"Valid PDF  : {res['is_valid_pdf']}")
        print(f"Expected   : {res['expected_hash']}")
        print(f"Actual     : {res['actual_hash']}")
        print(f"PDF Path   : {res['pdf_path']}")


# ── DB commands ───────────────────────────────────────────────────────────────

def cmd_db_health():
    print("Database Health Check")
    print(f"Path: {config.DATASET_DB_PATH}")
    exists = os.path.exists(config.DATASET_DB_PATH)
    print(f"Exists: {exists}")
    if not exists:
        return
    size_mb = os.path.getsize(config.DATASET_DB_PATH) / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")
    try:
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            tables = cur.fetchone()[0]
            print(f"Tables: {tables}")
            try:
                cur.execute("CREATE TABLE _test_ro (id INT)")
                print("Read-only: False (WARNING)")
            except Exception as e:
                if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                    print("Read-only: True")
                else:
                    print(f"Read-only check error: {e}")
    except Exception as e:
        print(f"Connection failed: {e}")


def cmd_db_schema():
    try:
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for (name,) in cur.fetchall():
                print(f"Table: {name}")
                print("-" * 40)
    except Exception as e:
        print(f"Schema dump failed: {e}")


# ── System status ─────────────────────────────────────────────────────────────

def cmd_system_status():
    print(HEADER)
    print("  System Status")
    print(HEADER)
    print(f"  Python Version       : {sys.version.split()[0]}")
    print(f"  Project Version      : 1.0.0 (Final)")

    dataset_avail = dataset_readonly = False
    try:
        with get_dataset_connection() as conn:
            dataset_avail = True
            try:
                conn.execute("CREATE TABLE _test_ro (id INT)")
                dataset_readonly = False
            except Exception as e:
                if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                    dataset_readonly = True
    except Exception:
        pass

    print(f"  Dataset DB Available : {dataset_avail}")
    print(f"  Dataset DB Read-Only : {dataset_readonly}")
    print(f"  Dataset Path         : {config.DATASET_DB_PATH}")

    op_avail = False
    try:
        from database.connection import get_operational_connection
        with get_operational_connection() as conn:
            op_avail = True
    except Exception:
        pass
    print(f"  Operational DB       : {'Available' if op_avail else 'Unavailable'}")

    # Table status
    table_status = {}
    if dataset_avail:
        try:
            with get_dataset_connection() as conn:
                cur = conn.cursor()
                for t in ["transactions", "profiles", "scenarios", "atms", "districts", "state_stats"]:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {t}")
                        table_status[t] = f"OK ({cur.fetchone()[0]} rows)"
                    except Exception as e:
                        table_status[t] = f"ERROR: {e}"
        except Exception:
            pass
    for t, status in table_status.items():
        print(f"  [{t}] {status}")

    llm_status = "ACTIVE" if LLMService.is_available() else "UNAVAILABLE (set MISTRAL_API_KEY in .env)"
    print(f"  Mistral LLM          : {llm_status}")
    print(f"  Mistral Model        : {config.MISTRAL_MODEL}")
    print(f"  Max Iterations       : {config.MAX_ITERATIONS}")
    print(f"  Max Tool Calls       : {config.MAX_TOOL_CALLS}")
    print(HEADER)


# ── Evaluate ──────────────────────────────────────────────────────────────────

def cmd_evaluate_investigation(investigation_id: str):
    print(HEADER)
    print("  Investigation Evaluation")
    print(HEADER)
    repo = OperationalRepository()
    inv_status = repo.get_investigation_status(investigation_id)
    evidence = repo.get_evidence_by_investigation(investigation_id)
    findings = repo.get_findings_by_investigation(investigation_id)
    result_dict = {
        "investigation_id": investigation_id,
        "status": inv_status.get("status", "UNKNOWN") if inv_status else "UNKNOWN",
        "evidence": evidence,
        "findings": findings,
        "risk_assessments": [],
        "tool_calls": 10,
    }
    eval_res = EvaluationEngine.evaluate(result_dict)
    print(f"\n  Overall Score         : {eval_res.overall_score}/100")
    print(f"  Evidence Quality      : {eval_res.evidence_quality_score}/100")
    print(f"  Evidence Completeness : {eval_res.evidence_completeness_score}/100")
    print(f"  Finding Consistency   : {eval_res.finding_consistency_score}/100")
    print(f"  Risk Consistency      : {eval_res.risk_consistency_score}/100")
    print(f"  Provenance Score      : {eval_res.provenance_score}/100")
    print(f"  Efficiency Score      : {eval_res.efficiency_score}/100")
    if eval_res.warnings:
        print("\n  Warnings:")
        for w in eval_res.warnings:
            print(f"  - {w}")
    if eval_res.failures:
        print("\n  Failures:")
        for f in eval_res.failures:
            print(f"  - {f}")
    print(HEADER)


# ── Argument parser ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Predictive Cybercrime Cash Withdrawal Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Primary usage:
  python -m cli.main investigate              (interactive mode — recommended)
  python -m cli.main investigate scenario SCENARIO_001  (scripted mode)
  python -m cli.main system status
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # db
    db_parser = subparsers.add_parser("db")
    db_sub = db_parser.add_subparsers(dest="db_command")
    db_sub.add_parser("health")
    db_sub.add_parser("schema")

    # investigate
    inv_parser = subparsers.add_parser("investigate")
    inv_parser.add_argument("--max-iterations", type=int, default=15)
    inv_parser.add_argument("--max-tool-calls", type=int, default=20)
    inv_sub = inv_parser.add_subparsers(dest="inv_command")
    scenario_parser = inv_sub.add_parser("scenario")
    scenario_parser.add_argument("scenario_id", type=str)
    scenario_parser.add_argument("--verbose", action="store_true")

    # report
    rep_parser = subparsers.add_parser("report")
    rep_sub = rep_parser.add_subparsers(dest="rep_command")
    rep_inv = rep_sub.add_parser("investigation")
    rep_inv.add_argument("investigation_id", type=str)
    rep_inv.add_argument("--output", type=str, default="reports")
    rep_ver = rep_sub.add_parser("verify")
    rep_ver.add_argument("report_id", type=str)

    # evaluate
    eval_parser = subparsers.add_parser("evaluate")
    eval_sub = eval_parser.add_subparsers(dest="eval_command")
    eval_inv = eval_sub.add_parser("investigation")
    eval_inv.add_argument("investigation_id", type=str)

    # system
    sys_parser = subparsers.add_parser("system")
    sys_sub = sys_parser.add_subparsers(dest="sys_command")
    sys_sub.add_parser("status")

    args = parser.parse_args()

    if args.command == "db":
        if args.db_command == "health":
            cmd_db_health()
        elif args.db_command == "schema":
            cmd_db_schema()
        else:
            db_parser.print_help()

    elif args.command == "investigate":
        if args.inv_command == "scenario":
            cmd_investigate(
                args.scenario_id,
                args.max_iterations,
                args.max_tool_calls,
                getattr(args, "verbose", False),
            )
        else:
            # Default: interactive mode
            cmd_investigate_interactive(
                max_iterations=args.max_iterations,
                max_tool_calls=args.max_tool_calls,
            )

    elif args.command == "report":
        if args.rep_command == "investigation":
            cmd_report_investigation(args.investigation_id, args.output)
        elif args.rep_command == "verify":
            cmd_report_verify(args.report_id)
        else:
            rep_parser.print_help()

    elif args.command == "evaluate":
        if args.eval_command == "investigation":
            cmd_evaluate_investigation(args.investigation_id)
        else:
            eval_parser.print_help()

    elif args.command == "system":
        if args.sys_command == "status":
            cmd_system_status()
        else:
            sys_parser.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
