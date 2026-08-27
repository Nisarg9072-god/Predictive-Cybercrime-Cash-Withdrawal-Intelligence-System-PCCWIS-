import json
from typing import List, Dict, Any, Optional
from database.connection import get_dataset_connection, get_operational_connection
from database import queries
from database.models import (
    TransactionSummary, ProfileSummary, ATMRecord, 
    ScenarioSummary, DistrictSummary, StateRiskSummary, TransactionChainSummary
)
from security.sanitizer import Sanitizer

DEFAULT_LIMIT = 50
MAX_LIMIT = 500

class DatasetRepository:
    """Repository for querying the master dataset in read-only mode."""
    
    @staticmethod
    def _enforce_limit(limit: int) -> int:
        return min(max(1, limit), MAX_LIMIT)

    @staticmethod
    def search_transactions(from_account: str = None, to_account: str = None, limit: int = DEFAULT_LIMIT, offset: int = 0) -> List[TransactionSummary]:
        limit = DatasetRepository._enforce_limit(limit)
        results = []
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            if from_account and to_account:
                cur.execute(queries.GET_TXNS_BY_ACCOUNT, (from_account, to_account, limit, offset))
            elif from_account:
                cur.execute("SELECT * FROM transactions WHERE from_account_id = ? LIMIT ? OFFSET ?", (from_account, limit, offset))
            elif to_account:
                cur.execute("SELECT * FROM transactions WHERE to_account_id = ? LIMIT ? OFFSET ?", (to_account, limit, offset))
            else:
                return []
            
            for row in cur.fetchall():
                results.append(TransactionSummary(**dict(row)))
        return results

    @staticmethod
    def get_transaction(txn_id: str) -> Optional[TransactionSummary]:
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_TRANSACTION_BY_ID, (txn_id,))
            row = cur.fetchone()
            if row:
                return TransactionSummary(**dict(row))
        return None

    @staticmethod
    def get_transaction_chain(chain_id: str, limit: int = DEFAULT_LIMIT) -> List[TransactionSummary]:
        limit = DatasetRepository._enforce_limit(limit)
        results = []
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_TRANSACTION_CHAIN, (chain_id, limit))
            for row in cur.fetchall():
                results.append(TransactionSummary(**dict(row)))
        return results

    @staticmethod
    def get_profile(identifier: str) -> Optional[ProfileSummary]:
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_PROFILE, (identifier, identifier))
            row = cur.fetchone()
            if row:
                sanitized_data = Sanitizer.sanitize_profile(dict(row))
                return ProfileSummary(**sanitized_data)
        return None

    @staticmethod
    def get_mule_profiles(limit: int = DEFAULT_LIMIT, offset: int = 0) -> List[ProfileSummary]:
        limit = DatasetRepository._enforce_limit(limit)
        results = []
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_MULE_PROFILES, (limit, offset))
            for row in cur.fetchall():
                sanitized_data = Sanitizer.sanitize_profile(dict(row))
                results.append(ProfileSummary(**sanitized_data))
        return results
        
    @staticmethod
    def get_atm(atm_id: str) -> Optional[ATMRecord]:
        """Returns ATM record. Returns None gracefully if the table is malformed (known corruption)."""
        try:
            with get_dataset_connection() as conn:
                cur = conn.cursor()
                cur.execute(queries.GET_ATM_BY_ID, (atm_id,))
                row = cur.fetchone()
                if row:
                    return ATMRecord(**dict(row))
        except Exception:
            # ATM table has known disk image corruption — return None, caller shows BLOCKED
            return None
        return None

    @staticmethod
    def get_scenario(scenario_id: str) -> Optional[ScenarioSummary]:
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_SCENARIO, (scenario_id,))
            row = cur.fetchone()
            if row:
                # We can also fetch data_json but scenario summary excludes it to prevent bloat
                return ScenarioSummary(**dict(row))
        return None

    @staticmethod
    def get_scenario_raw(scenario_id: str) -> Optional[Dict[str, Any]]:
        """Returns scenario metadata dict. Excludes data_json (known corruption)."""
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_SCENARIO_SAFE, (scenario_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def search_by_account_pattern(pattern: str, limit: int = 20) -> List[TransactionSummary]:
        """Find transactions where an account_id partially matches 'pattern' (for victim account discovery)."""
        limit = DatasetRepository._enforce_limit(limit)
        wildcard = f"%{pattern}%"
        results = []
        with get_dataset_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.SEARCH_TXNS_BY_ACCOUNT_PATTERN, (wildcard, wildcard, limit, 0))
            for row in cur.fetchall():
                try:
                    results.append(TransactionSummary(**dict(row)))
                except Exception:
                    continue
        return results

class OperationalRepository:
    """Repository for managing agent operational state."""
    
    @staticmethod
    def execute_insert(query: str, params: tuple):
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()

    @staticmethod
    def execute_update(query: str, params: tuple):
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()

    @staticmethod
    def log_risk_assessment(assessment: dict):
        OperationalRepository.execute_insert(queries.INSERT_RISK_ASSESSMENT, (
            assessment["risk_assessment_id"],
            assessment["investigation_id"],
            assessment["iteration"],
            assessment["risk_score"],
            assessment["risk_level"],
            assessment["confidence"],
            assessment["indicator_ids"],
            assessment["evidence_ids"],
            assessment["created_at"]
        ))

    # Phase 5: Evidence Management
    def save_evidence(self, evidence_item: Any) -> None:
        """Persist an EvidenceRecord to the operational database."""
        with get_operational_connection() as conn:
            cur = conn.cursor()
            # Check if hash already exists (deduplication at DB layer)
            cur.execute(queries.GET_EVIDENCE_BY_HASH, (evidence_item.hash,))
            if cur.fetchone():
                return  # Duplicate hash, ignore

            cur.execute(queries.INSERT_EVIDENCE, (
                evidence_item.evidence_id,
                evidence_item.investigation_id,
                evidence_item.source_type,
                evidence_item.source_id,
                evidence_item.observed_field,
                str(evidence_item.observed_value),
                evidence_item.description,
                evidence_item.confidence,
                evidence_item.timestamp,
                evidence_item.hash,
                evidence_item.classification.value,
                evidence_item.indicator_name,
                evidence_item.parent_evidence_id,
                evidence_item.timestamp  # created_at
            ))
            conn.commit()

    def get_evidence_by_investigation(self, investigation_id: str) -> List[Dict[str, Any]]:
        results = []
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_EVIDENCE_BY_INVESTIGATION, (investigation_id,))
            for row in cur.fetchall():
                results.append(dict(row))
        return results

    # Phase 5: Report Persistence
    def save_report(self, report_record: Any) -> None:
        self.execute_insert(queries.INSERT_REPORT, (
            report_record.report_id,
            report_record.investigation_id,
            report_record.scenario_id,
            report_record.mode,
            report_record.pdf_path,
            report_record.sha256,
            report_record.generated_at
        ))

    def get_report_by_id(self, report_id: str) -> Optional[Any]:
        from reporting.models import ReportRecord
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_REPORT_BY_ID, (report_id,))
            row = cur.fetchone()
            if row:
                return ReportRecord(**dict(row))
        return None

    def list_reports_by_investigation(self, investigation_id: str) -> List[Any]:
        from reporting.models import ReportRecord
        results = []
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.LIST_REPORTS_BY_INVESTIGATION, (investigation_id,))
            for row in cur.fetchall():
                results.append(ReportRecord(**dict(row)))
        return results

    # Phase 5: Finding Lifecycle
    def log_finding_transition(self, transition: Any) -> None:
        self.execute_insert(queries.INSERT_FINDING_TRANSITION, (
            transition.transition_id,
            transition.finding_id,
            transition.investigation_id,
            transition.from_status,
            transition.to_status,
            transition.reason,
            transition.transitioned_at,
            transition.transitioned_by
        ))

    def get_findings_by_investigation(self, investigation_id: str) -> List[Dict[str, Any]]:
        results = []
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute(queries.GET_FINDINGS_BY_INVESTIGATION, (investigation_id,))
            for row in cur.fetchall():
                d = dict(row)
                if d.get("indicator_ids"):
                    d["indicator_ids"] = json.loads(d["indicator_ids"])
                if d.get("evidence_ids"):
                    d["evidence_ids"] = json.loads(d["evidence_ids"])
                if d.get("recommendations"):
                    d["recommendations"] = json.loads(d["recommendations"])
                results.append(d)
        return results

    def get_investigation_status(self, investigation_id: str) -> Dict[str, Any]:
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM investigations WHERE investigation_id = ?", (investigation_id,))
            row = cur.fetchone()
            if row:
                return {"investigation_id": investigation_id, "status": row["status"]}
        return {"investigation_id": investigation_id, "status": "UNKNOWN"}
