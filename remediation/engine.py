"""
remediation/engine.py — Maps finding categories to structured recommendations.

All recommendations are clearly labelled RECOMMENDATION.
They are never presented as confirmed facts or proven actions.
"""

from typing import Dict, List


class RemediationEngine:
    """
    Deterministic recommendation generator.
    Maps finding category → list of structured recommendation dicts.
    """

    # All recommendation strings are labelled RECOMMENDATION (not facts).
    _RECOMMENDATIONS: Dict[str, List[Dict]] = {
        "TRANSACTION_LAUNDERING_PATTERN": [
            {
                "code":     "REC-LAU-001",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Flag all transactions in the identified chain for manual expert review.",
                "rationale": "Laundering indicators were observed across multiple hops. Expert review is required before any enforcement action.",
            },
            {
                "code":     "REC-LAU-002",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Cross-reference flagged accounts against existing watchlists and STR filings.",
                "rationale": "Overlapping account identifiers may appear in prior Suspicious Transaction Reports.",
            },
            {
                "code":     "REC-LAU-003",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Review transaction velocity thresholds for accounts in the flagged chain.",
                "rationale": "High-velocity transactions may indicate automated layering behaviour.",
            },
        ],
        "TERMINAL_CASHOUT_RISK": [
            {
                "code":     "REC-CASH-001",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Identify the terminal ATM location and assess operational status.",
                "rationale": "Terminal cashout events indicate the end of a potential mule chain. Physical location context is relevant.",
            },
            {
                "code":     "REC-CASH-002",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Alert relevant financial institution's fraud team for the involved accounts.",
                "rationale": "Cashout events may still be in progress during a golden-hour scenario.",
            },
            {
                "code":     "REC-CASH-003",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Consider geographic clustering of the ATM with other flagged cashout locations.",
                "rationale": "Organised crime networks often use a small cluster of ATMs for terminal cashouts.",
            },
        ],
        "MULTI_HOP_TRANSFER_PATTERN": [
            {
                "code":     "REC-HOP-001",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Trace the complete transaction chain to identify all intermediate accounts.",
                "rationale": "Multi-hop layering is used to obscure the origin of funds. Each hop increases complexity.",
            },
            {
                "code":     "REC-HOP-002",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Perform additional account verification (e.g., KYC review) on all intermediate accounts.",
                "rationale": "Mule accounts often pass through multiple legitimate-appearing accounts before cashout.",
            },
            {
                "code":     "REC-HOP-003",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Investigate linked transaction chains originating from the same source account.",
                "rationale": "The same source may fund multiple parallel chains to distribute risk.",
            },
        ],
        "MULE_ACCOUNT_RISK": [
            {
                "code":     "REC-MULE-001",
                "priority": "HIGH",
                "label":    "RECOMMENDATION",
                "action":   "Refer the flagged mule account profile for enhanced due diligence.",
                "rationale": "Account is flagged as mule in dataset. Manual review is required before any action — this is a data flag, not proof.",
            },
            {
                "code":     "REC-MULE-002",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Review transaction history of linked accounts for corroborating evidence.",
                "rationale": "Mule accounts typically operate in clusters. Corroborating transaction evidence strengthens the case.",
            },
        ],
        "HIGH_VALUE_TRANSFER": [
            {
                "code":     "REC-HVT-001",
                "priority": "MEDIUM",
                "label":    "RECOMMENDATION",
                "action":   "Verify purpose and documentation for high-value transfers exceeding INR 50,000.",
                "rationale": "High-value transfers without documented purpose may warrant further scrutiny.",
            },
        ],
        "UNUSUAL_TRANSACTION_PATTERN": [
            {
                "code":     "REC-UTP-001",
                "priority": "LOW",
                "label":    "RECOMMENDATION",
                "action":   "Monitor the associated accounts for sustained unusual activity.",
                "rationale": "Unusual patterns require longitudinal monitoring before conclusions can be drawn.",
            },
        ],
    }

    _DEFAULT_RECOMMENDATIONS = [
        {
            "code":     "REC-GEN-001",
            "priority": "LOW",
            "label":    "RECOMMENDATION",
            "action":   "Retain all evidence records for the investigation period as per data retention policy.",
            "rationale": "Evidence must be preserved for potential regulatory or legal review.",
        },
    ]

    @classmethod
    def get_recommendations(cls, category: str) -> List[Dict]:
        """Returns structured recommendations for a finding category."""
        return cls._RECOMMENDATIONS.get(category, cls._DEFAULT_RECOMMENDATIONS)

    @classmethod
    def format_for_report(cls, category: str) -> str:
        """Returns formatted recommendation text for PDF/display."""
        recs = cls.get_recommendations(category)
        lines = []
        for rec in recs:
            lines.append(
                f"[{rec['label']}] [{rec['priority']}] {rec['code']}\n"
                f"  Action:    {rec['action']}\n"
                f"  Rationale: {rec['rationale']}"
            )
        return "\n\n".join(lines)
