from typing import Dict, Any, List

class IndicatorEngine:
    """Evaluates features to generate deterministic cybercrime indicators."""
    
    @staticmethod
    def generate_indicators(features: Dict[str, Any], source: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Maps features into discrete indicators.
        Each indicator includes name, value, threshold, observed_value, and confidence.
        All thresholds are PROJECT HEURISTICs unless noted otherwise.
        """
        indicators = []
        
        # ── Transaction Indicators ──────────────────────────────────────────
        if features.get("laundering_count", 0) > 0:
            indicators.append({
                "indicator_id": "IND_LAUNDERING_FLAG",
                "name": "LAUNDERING_FLAG",
                "value": True,
                "threshold": ">0  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["is_laundering"],
                "observed_value": features["laundering_count"],
                "description": f"Found {features['laundering_count']} transactions explicitly flagged as laundering.",
                "confidence": 0.95
            })
            
        if features.get("terminal_cashout_count", 0) > 0:
            indicators.append({
                "indicator_id": "IND_TERMINAL_CASHOUT",
                "name": "TERMINAL_CASHOUT",
                "value": True,
                "threshold": ">0  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["is_terminal_cashout"],
                "observed_value": features["terminal_cashout_count"],
                "description": f"Terminal cashout detected in {features['terminal_cashout_count']} transactions.",
                "confidence": 0.95
            })
            
        if features.get("has_high_value"):
            indicators.append({
                "indicator_id": "IND_HIGH_VALUE_TRANSFER",
                "name": "HIGH_VALUE_TRANSFER",
                "value": True,
                "threshold": "amount_inr > 50000  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["amount_inr"],
                "observed_value": features.get("avg_amount", 0),
                "description": "At least one transaction exceeds 50,000 INR.",
                "confidence": 0.80
            })
            
        if features.get("unique_counterparties", 0) >= 3:
            indicators.append({
                "indicator_id": "IND_MULTIPLE_COUNTERPARTIES",
                "name": "MULTIPLE_COUNTERPARTIES",
                "value": True,
                "threshold": "unique_counterparties >= 3  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["from_account_id", "to_account_id"],
                "observed_value": features["unique_counterparties"],
                "description": f"Transacted with {features['unique_counterparties']} distinct counterparties.",
                "confidence": 0.70
            })

        # ── Profile Indicators ────────────────────────────────────────────────
        if features.get("mule_count", 0) > 0:
            indicators.append({
                "indicator_id": "IND_HIGH_RISK_PROFILE",
                "name": "HIGH_RISK_PROFILE",
                "value": True,
                "threshold": "is_mule = 1  [DATA-DRIVEN — flag from dataset]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["is_mule"],
                "observed_value": features["mule_count"],
                "description": f"{features['mule_count']} profile(s) explicitly flagged as mule in dataset.",
                "confidence": 0.90
            })
            
        if features.get("has_new_account") and features.get("has_high_velocity"):
            indicators.append({
                "indicator_id": "IND_NEW_ACCOUNT_HIGH_ACTIVITY",
                "name": "NEW_ACCOUNT_HIGH_ACTIVITY",
                "value": True,
                "threshold": "account_age_days < 30 AND withdrawal_velocity_per_day > 50000  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["account_age_days", "withdrawal_velocity_per_day"],
                "observed_value": {"new_account": features["has_new_account"], "high_velocity": features["has_high_velocity"]},
                "description": "New account (<30 days) with high withdrawal velocity observed.",
                "confidence": 0.85
            })
            
        elif features.get("has_high_velocity"):
            indicators.append({
                "indicator_id": "IND_RAPID_TRANSACTION_VELOCITY",
                "name": "RAPID_TRANSACTION_VELOCITY",
                "value": True,
                "threshold": "withdrawal_velocity_per_day > 50000  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["withdrawal_velocity_per_day"],
                "observed_value": features.get("has_high_velocity"),
                "description": "Account demonstrates rapid withdrawal velocity (>50,000 INR/day).",
                "confidence": 0.75
            })

        # ── Chain Indicators ───────────────────────────────────────────────────
        if features.get("multi_hop_presence"):
            indicators.append({
                "indicator_id": "IND_MULTI_HOP_CHAIN",
                "name": "MULTI_HOP_CHAIN",
                "value": True,
                "threshold": "hop_count >= 3  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["hop_layer"],
                "observed_value": features.get("max_chain_length", "unknown"),
                "description": f"Multi-hop transaction chain detected (max hops: {features.get('max_chain_length', 'unknown')}).",
                "confidence": 0.85
            })
            
        # ── Geographic Indicators ─────────────────────────────────────────────
        if features.get("high_risk_state_presence"):
            indicators.append({
                "indicator_id": "IND_GEOGRAPHIC_RISK_CONTEXT",
                "name": "GEOGRAPHIC_RISK_CONTEXT",
                "value": True,
                "threshold": "risk_tier in [HIGH, CRITICAL]  [PROJECT HEURISTIC]",
                "source": source,
                "source_id": source_id,
                "supporting_fields": ["risk_tier"],
                "observed_value": features.get("max_incident_density", 0),
                "description": "Involved entity located in high-risk geographic region (contextual, not proof of activity).",
                "confidence": 0.60
            })
            
        return indicators
