"""
evidence/collector.py — Extracts EvidenceItems from the agent's investigation state.

Each tool result produces one or more structured EvidenceItem objects.
All items are OBSERVED (direct field reads) or DERIVED (computed aggregates).
"""

import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List

from .models import EvidenceClassification, EvidenceItem


class EvidenceCollector:
    """
    Converts raw agent tool results into structured EvidenceItem objects.
    Replaces the ad-hoc {"evidence_id": ..., "observation": ...} dicts in nodes.py.
    """

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _make(
        investigation_id: str,
        source_type: str,
        source_id: str,
        observed_field: str,
        observed_value: Any,
        description: str,
        confidence: float,
        classification: EvidenceClassification = EvidenceClassification.OBSERVED,
        indicator_name: str | None = None,
    ) -> EvidenceItem:
        eid = str(uuid.uuid4())
        return EvidenceItem.create(
            evidence_id=eid,
            investigation_id=investigation_id,
            source_type=source_type,
            source_id=source_id,
            observed_field=observed_field,
            observed_value=observed_value,
            description=description,
            confidence=confidence,
            classification=classification,
            indicator_name=indicator_name,
        )

    @classmethod
    def from_scenario(
        cls, investigation_id: str, scenario_id: str, data: dict
    ) -> List[EvidenceItem]:
        items = []
        items.append(cls._make(
            investigation_id, "SCENARIO", scenario_id,
            "scenario_id", scenario_id,
            f"Scenario {scenario_id} loaded from database.",
            confidence=1.0,
        ))
        if data.get("crime_category"):
            items.append(cls._make(
                investigation_id, "SCENARIO", scenario_id,
                "crime_category", data["crime_category"],
                f"Crime category: {data['crime_category']}",
                confidence=1.0,
            ))
        if data.get("amount_lost_inr"):
            items.append(cls._make(
                investigation_id, "SCENARIO", scenario_id,
                "amount_lost_inr", data["amount_lost_inr"],
                f"Reported victim loss: INR {data['amount_lost_inr']:,.0f}",
                confidence=1.0,
            ))
        return items

    @classmethod
    def from_transactions(
        cls, investigation_id: str, transactions: List[dict]
    ) -> List[EvidenceItem]:
        items = []
        count = len(transactions)
        laundering = sum(1 for t in transactions if t.get("is_laundering", 0))
        cashouts   = sum(1 for t in transactions if t.get("is_terminal_cashout", 0))

        for t in transactions:
            txn_id = t.get("txn_id", "unknown")
            if t.get("is_laundering"):
                items.append(cls._make(
                    investigation_id, "TRANSACTION", txn_id,
                    "is_laundering", 1,
                    f"Transaction {txn_id} carries laundering flag.",
                    confidence=0.95,
                    indicator_name="LAUNDERING_FLAG",
                ))
            if t.get("is_terminal_cashout"):
                items.append(cls._make(
                    investigation_id, "TRANSACTION", txn_id,
                    "is_terminal_cashout", 1,
                    f"Transaction {txn_id} is a terminal cashout.",
                    confidence=0.95,
                    indicator_name="TERMINAL_CASHOUT",
                ))
            if t.get("amount_inr", 0) > 50000:
                items.append(cls._make(
                    investigation_id, "TRANSACTION", txn_id,
                    "amount_inr", t["amount_inr"],
                    f"High-value transfer: INR {t['amount_inr']:,.0f}.",
                    confidence=0.80,
                    indicator_name="HIGH_VALUE_TRANSFER",
                ))

        # Aggregated DERIVED evidence
        if count > 0:
            items.append(cls._make(
                investigation_id, "TRANSACTION_AGGREGATE", "AGGREGATE",
                "transaction_count", count,
                f"{count} transactions observed. {laundering} flagged as laundering, {cashouts} terminal cashout(s).",
                confidence=1.0,
                classification=EvidenceClassification.DERIVED,
            ))
        return items

    @classmethod
    def from_profile(
        cls, investigation_id: str, profile: dict
    ) -> List[EvidenceItem]:
        items = []
        acc_id = profile.get("account_id", "unknown")
        prof_id = profile.get("profile_id", acc_id)

        if profile.get("is_mule", 0):
            items.append(cls._make(
                investigation_id, "PROFILE", prof_id,
                "is_mule", 1,
                f"Account {acc_id[-4:] if len(acc_id) > 4 else '****'} is flagged as a mule account in dataset.",
                confidence=0.90,
                indicator_name="HIGH_RISK_PROFILE",
            ))
        if profile.get("withdrawal_velocity_per_day", 0) > 50000:
            items.append(cls._make(
                investigation_id, "PROFILE", prof_id,
                "withdrawal_velocity_per_day", profile["withdrawal_velocity_per_day"],
                f"High daily withdrawal velocity observed.",
                confidence=0.80,
                indicator_name="RAPID_TRANSACTION_VELOCITY",
            ))
        if profile.get("account_age_days", 365) < 30:
            items.append(cls._make(
                investigation_id, "PROFILE", prof_id,
                "account_age_days", profile["account_age_days"],
                f"Account is less than 30 days old.",
                confidence=0.75,
                indicator_name="NEW_ACCOUNT_HIGH_ACTIVITY",
            ))
        # Always emit a base profile observation
        items.append(cls._make(
            investigation_id, "PROFILE", prof_id,
            "kyc_status", profile.get("kyc_status", "UNKNOWN"),
            f"Profile loaded: KYC status = {profile.get('kyc_status', 'UNKNOWN')}.",
            confidence=0.90,
        ))
        return items

    @classmethod
    def from_chain(
        cls, investigation_id: str, chain_transactions: List[dict]
    ) -> List[EvidenceItem]:
        items = []
        if not chain_transactions:
            return items
        hops = max((t.get("hop_layer", 0) for t in chain_transactions), default=0)
        chain_id = chain_transactions[0].get("chain_id", "unknown")
        items.append(cls._make(
            investigation_id, "TRANSACTION_CHAIN", chain_id,
            "hop_layer", hops,
            f"Transaction chain traced to hop depth {hops}.",
            confidence=0.90,
            classification=EvidenceClassification.DERIVED,
            indicator_name="MULTI_HOP_CHAIN" if hops >= 3 else None,
        ))
        return items

    @classmethod
    def from_atm(
        cls, investigation_id: str, atm: dict
    ) -> List[EvidenceItem]:
        items = []
        atm_id = atm.get("atm_id", "unknown")
        items.append(cls._make(
            investigation_id, "ATM", atm_id,
            "operational_status", atm.get("operational_status", "UNKNOWN"),
            f"ATM {atm_id}: status={atm.get('operational_status','?')} "
            f"cash_index={atm.get('cash_availability_index','?')}.",
            confidence=0.85,
        ))
        if atm.get("cash_availability_index", 1.0) < 0.2:
            items.append(cls._make(
                investigation_id, "ATM", atm_id,
                "cash_availability_index", atm["cash_availability_index"],
                f"ATM has very low cash availability — potential high-demand withdrawal point.",
                confidence=0.70,
                classification=EvidenceClassification.DERIVED,
            ))
        return items

    @classmethod
    def from_mule_profiles(
        cls, investigation_id: str, profiles: List[dict]
    ) -> List[EvidenceItem]:
        items = []
        for p in profiles:
            items.extend(cls.from_profile(investigation_id, p))
        return items
