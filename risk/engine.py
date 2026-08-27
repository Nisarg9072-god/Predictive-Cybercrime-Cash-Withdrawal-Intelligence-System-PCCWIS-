"""
risk/engine.py — Deterministic Cybercrime Risk Engine

PROJECT RISK THRESHOLDS (not statistically validated):
  0-24   LOW      : Minimal indicators. Insufficient evidence to support concern.
  25-49  MODERATE : Some indicators present. Warrants monitoring.
  50-74  HIGH     : Multiple indicators. Warrants investigation.
  75-100 CRITICAL : Strong corroborating evidence across multiple dimensions.

RISK SCORE FORMULA (PROJECT HEURISTIC):
  score = 0
  + 30 if LAUNDERING_FLAG indicator present  (txn-level data flag, high weight)
  + 25 if HIGH_RISK_PROFILE indicator present (mule account explicitly flagged)
  + 20 if TERMINAL_CASHOUT indicator present  (end-of-chain cashout detected)
  + 15 if MULTI_HOP_CHAIN indicator present   (layered transfer chain >= 3 hops)
  + 10 if RAPID_TRANSACTION_VELOCITY present  (velocity > 50,000 INR/day)
  Capped at 100.

CONFIDENCE FORMULA (PROJECT HEURISTIC):
  base_confidence = 0.10
  + 0.15 per independent indicator (from distinct feature dimensions)
  Capped at 0.95
  Adjusted DOWN if contradictory evidence is detected (see below).

CONTRADICTORY EVIDENCE RULE:
  Trigger: HIGH_RISK_PROFILE present AND no LAUNDERING_FLAG, TERMINAL_CASHOUT,
           or MULTI_HOP_CHAIN present AND transaction_count > 0.
  Interpretation: Evidence A = profile suggests mule. Evidence B = transaction
                  history does not exhibit laundering patterns.
  Effect:
    score -= 15
    confidence -= 0.20
    risk_level recategorized downward if threshold crossed
  Status of resulting finding: INCONCLUSIVE (if confidence < 0.50)

MACHINE-READABLE EXPLANATION:
  Every calculate_risk() call returns:
  {
    "risk_score": float,         # 0-100
    "risk_level": str,           # LOW/MODERATE/HIGH/CRITICAL
    "confidence": float,         # 0.0-0.95
    "indicators": [              # list of active indicators with full evidence trace
      {
        "indicator_id": str,
        "name": str,
        "value": any,
        "threshold": str,
        "source": str,
        "source_id": str,
        "supporting_fields": list,
        "observed_value": any,   # actual value that triggered the indicator
        "description": str,
        "confidence": float
      }
    ],
    "features": dict,            # raw feature values extracted
    "contradictory_evidence": bool
  }
"""

from typing import Dict, Any, List, Optional
import uuid
from database.models import TransactionSummary, ProfileSummary, TransactionChainSummary, ATMRecord
from .transaction_features import TransactionFeatureExtractor
from .profile_features import ProfileFeatureExtractor
from .chain_features import ChainFeatureExtractor
from .atm_features import ATMFeatureExtractor
from .geographic_features import GeographicFeatureExtractor
from .indicators import IndicatorEngine


class RiskEngine:
    """
    Deterministic, evidence-backed cybercrime risk assessment engine.

    Key guarantees:
      - Given the same state, produces identical risk_score, risk_level, confidence.
      - No LLM calls. All values are computed from structured data.
      - Contradictory evidence is handled by an explicit documented rule.
      - Every indicator is traceable to its source data field.
    """

    # PROJECT RISK THRESHOLDS (see module docstring for rationale)
    LEVEL_CRITICAL_THRESHOLD = 75
    LEVEL_HIGH_THRESHOLD = 50
    LEVEL_MODERATE_THRESHOLD = 25

    # Indicator weights (PROJECT HEURISTIC)
    WEIGHTS = {
        "LAUNDERING_FLAG": 30,
        "HIGH_RISK_PROFILE": 25,
        "TERMINAL_CASHOUT": 20,
        "MULTI_HOP_CHAIN": 15,
        "RAPID_TRANSACTION_VELOCITY": 10,
        "HIGH_VALUE_TRANSFER": 5,
        "NEW_ACCOUNT_HIGH_ACTIVITY": 5,
        "MULTIPLE_COUNTERPARTIES": 5,
        "GEOGRAPHIC_RISK_CONTEXT": 5,
    }

    # Confidence base and per-indicator gain (PROJECT HEURISTIC)
    CONFIDENCE_BASE = 0.10
    CONFIDENCE_PER_INDICATOR = 0.15
    CONFIDENCE_MAX = 0.95

    # Contradictory evidence penalty (PROJECT HEURISTIC)
    CONTRADICTORY_SCORE_PENALTY = 15
    CONTRADICTORY_CONFIDENCE_PENALTY = 0.20

    @staticmethod
    def _coerce_models(state: Dict[str, Any]):
        """Safely coerce dicts or model instances from state."""
        def coerce(items, cls):
            result = []
            for item in items:
                try:
                    if isinstance(item, dict):
                        result.append(cls(**item))
                    elif isinstance(item, cls):
                        result.append(item)
                    # else skip unknown type silently
                except Exception:
                    pass  # Malformed data: skip, never invent
            return result

        transactions = coerce(state.get("transactions", []), TransactionSummary)
        profiles = coerce(state.get("profiles", []), ProfileSummary)
        chains = coerce(state.get("transaction_chains", []), TransactionChainSummary)
        atms = coerce(state.get("atms", []), ATMRecord)
        return transactions, profiles, chains, atms

    @staticmethod
    def calculate_risk(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic risk calculation.

        INPUT:  agent state dict containing transactions, profiles, chains, atms, evidence
        OUTPUT: {risk_score, risk_level, confidence, indicators, features, contradictory_evidence}
        """
        transactions, profiles, chains, atms = RiskEngine._coerce_models(state)

        # Extract features
        tx_features = TransactionFeatureExtractor.extract(transactions)
        prof_features = ProfileFeatureExtractor.extract(profiles)
        chain_features = ChainFeatureExtractor.extract(chains)
        atm_features = ATMFeatureExtractor.extract(atms)
        geo_features = GeographicFeatureExtractor.extract([])  # state_stats not yet in agent state

        all_features = {
            **tx_features,
            **prof_features,
            **chain_features,
            **atm_features,
            **geo_features,
        }

        # Generate indicators
        indicators = IndicatorEngine.generate_indicators(
            all_features,
            source="AGENT_STATE",
            source_id=state.get("investigation_id", "unknown")
        )

        # Build indicator name set for fast lookup
        active_names = {ind["name"] for ind in indicators}

        # Weighted risk score (PROJECT HEURISTIC)
        score = 0.0
        for name, weight in RiskEngine.WEIGHTS.items():
            if name in active_names:
                score += weight
        score = min(score, 100.0)

        # Risk level categorization
        if score >= RiskEngine.LEVEL_CRITICAL_THRESHOLD:
            level = "CRITICAL"
        elif score >= RiskEngine.LEVEL_HIGH_THRESHOLD:
            level = "HIGH"
        elif score >= RiskEngine.LEVEL_MODERATE_THRESHOLD:
            level = "MODERATE"
        else:
            level = "LOW"

        # Confidence score (PROJECT HEURISTIC)
        # Each indicator from a distinct dimension adds 0.15, capped at 0.95
        n_indicators = len(indicators)
        confidence = min(
            RiskEngine.CONFIDENCE_BASE + n_indicators * RiskEngine.CONFIDENCE_PER_INDICATOR,
            RiskEngine.CONFIDENCE_MAX,
        )
        if n_indicators == 0:
            confidence = 0.0

        # Contradictory evidence rule (PROJECT HEURISTIC, explicitly documented):
        #   Condition: profile is flagged as mule (supporting evidence: HIGH_RISK_PROFILE)
        #              BUT transaction data shows NO laundering flag, NO terminal cashout,
        #              NO multi-hop chain — and we do have actual transactions to evaluate.
        #   This means Evidence A and Evidence B disagree.
        #   Adjustment: reduce score by 15, reduce confidence by 0.20.
        contradictory = False
        if (
            "HIGH_RISK_PROFILE" in active_names
            and "LAUNDERING_FLAG" not in active_names
            and "TERMINAL_CASHOUT" not in active_names
            and "MULTI_HOP_CHAIN" not in active_names
            and tx_features["transaction_count"] > 0
        ):
            contradictory = True
            score = max(score - RiskEngine.CONTRADICTORY_SCORE_PENALTY, 0.0)
            confidence = max(confidence - RiskEngine.CONTRADICTORY_CONFIDENCE_PENALTY, 0.0)
            # Recategorize after adjustment
            if score >= RiskEngine.LEVEL_CRITICAL_THRESHOLD:
                level = "CRITICAL"
            elif score >= RiskEngine.LEVEL_HIGH_THRESHOLD:
                level = "HIGH"
            elif score >= RiskEngine.LEVEL_MODERATE_THRESHOLD:
                level = "MODERATE"
            else:
                level = "LOW"

        return {
            "risk_score": round(score, 2),
            "risk_level": level,
            "confidence": round(confidence, 2),
            "indicators": indicators,
            "features": all_features,
            "contradictory_evidence": contradictory,
        }

    @staticmethod
    def generate_finding(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Produces a structured finding when evidence is sufficient (risk_score >= 50).

        Returns None if insufficient evidence.
        Uses neutral language — never declares criminal guilt.
        """
        analysis = RiskEngine.calculate_risk(state)
        score = analysis["risk_score"]
        level = analysis["risk_level"]
        confidence = analysis["confidence"]
        indicators = analysis["indicators"]
        contradictory = analysis["contradictory_evidence"]

        if score < RiskEngine.LEVEL_HIGH_THRESHOLD:
            return None

        # Severity mirrors risk level (deterministic)
        severity = level

        # Status
        if contradictory or confidence < 0.50:
            status = "INCONCLUSIVE"
            title = "Observed indicators are inconclusive — insufficient corroborating evidence"
        elif score >= RiskEngine.LEVEL_CRITICAL_THRESHOLD:
            status = "CONFIRMED_PATTERN"
            title = "Evidence suggests a confirmed high-risk transaction pattern"
        else:
            status = "POTENTIAL_PATTERN"
            title = "Evidence is consistent with a potential cybercrime transaction pattern"

        # Category (deterministic priority order)
        active_names = {ind["name"] for ind in indicators}
        if "LAUNDERING_FLAG" in active_names:
            category = "TRANSACTION_LAUNDERING_PATTERN"
        elif "TERMINAL_CASHOUT" in active_names:
            category = "TERMINAL_CASHOUT_RISK"
        elif "MULTI_HOP_CHAIN" in active_names:
            category = "MULTI_HOP_TRANSFER_PATTERN"
        elif "HIGH_RISK_PROFILE" in active_names:
            category = "MULE_ACCOUNT_RISK"
        elif "HIGH_VALUE_TRANSFER" in active_names:
            category = "UNUSUAL_TRANSACTION_PATTERN"
        else:
            category = "UNUSUAL_TRANSACTION_PATTERN"

        # Explainability bullets
        why_bullets = [f"- {ind['description']}" for ind in indicators]
        explanation = "Why:\n" + "\n".join(why_bullets)

        evidence_ids = [e["evidence_id"] for e in state.get("evidence", [])]
        indicator_ids = [ind["indicator_id"] for ind in indicators]

        return {
            "finding_id": str(uuid.uuid4()),
            "investigation_id": state.get("investigation_id", "unknown"),
            "title": title,
            "category": category,
            "severity": severity,
            "confidence": confidence,
            "description": explanation,
            "indicator_ids": indicator_ids,
            "evidence_ids": evidence_ids,
            "risk_score": score,
            "contradictory_evidence": contradictory,
            "remediation": "Recommend manual expert review of flagged transactions and accounts.",
            "status": status,
            "machine_readable": {
                "risk_score": score,
                "risk_level": level,
                "confidence": confidence,
                "indicators": [ind["name"] for ind in indicators],
                "evidence_ids": evidence_ids,
            },
        }
