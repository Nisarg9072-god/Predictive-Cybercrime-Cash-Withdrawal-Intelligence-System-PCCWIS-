"""
evidence/formatter.py — Evidence display formatting with PII masking.

Applies security.sanitizer to all account IDs and sensitive identifiers
before rendering for terminal, PDF, or API output.
"""

from typing import List
from security.sanitizer import Sanitizer
from .models import EvidenceClassification, EvidenceItem


class EvidenceFormatter:
    """Formats EvidenceItem for display. Always masks PII."""

    # Fields that should have PII masked
    SENSITIVE_FIELDS = {"account_id", "from_account_id", "to_account_id", "profile_id"}

    @staticmethod
    def _mask_value(field: str, value: str) -> str:
        """Apply appropriate masking based on field name."""
        if not isinstance(value, str):
            return str(value)
        if "account" in field.lower():
            return Sanitizer.mask_account_number(value)
        if "phone" in field.lower():
            return Sanitizer.mask_phone_number(value)
        if "pan" in field.lower():
            return Sanitizer.mask_pan(value)
        return value

    @classmethod
    def format_short(cls, item: EvidenceItem) -> str:
        """Single-line format for terminal/audit trail."""
        masked_value = cls._mask_value(item.observed_field, str(item.observed_value))
        return (
            f"[{item.classification.value}] "
            f"{item.source_type}:{item.source_id[-8:] if len(item.source_id) > 8 else item.source_id}"
            f".{item.observed_field}={masked_value} "
            f"(conf={item.confidence:.2f})"
        )

    @classmethod
    def format_long(cls, item: EvidenceItem) -> str:
        """Multi-line format for PDF evidence block."""
        masked_value = cls._mask_value(item.observed_field, str(item.observed_value))
        lines = [
            f"Evidence ID : {item.evidence_id}",
            f"Source      : {item.source_type} / {item.source_id}",
            f"Field       : {item.observed_field}",
            f"Value       : {masked_value}",
            f"Description : {item.description}",
            f"Class       : {item.classification.value}",
            f"Confidence  : {item.confidence:.2f}",
            f"Timestamp   : {item.timestamp}",
            f"Hash        : {item.hash[:16]}…",
        ]
        if item.indicator_name:
            lines.insert(3, f"Indicator   : {item.indicator_name}")
        return "\n".join(lines)

    @classmethod
    def format_provenance_block(
        cls,
        finding_id: str,
        indicator_names: List[str],
        evidence_items: List[EvidenceItem],
    ) -> str:
        """
        Full provenance chain block:
        Finding → Indicator → Evidence → Database source → Source record
        """
        lines = [
            f"Finding: {finding_id}",
            "  │",
        ]
        for ind in indicator_names:
            lines.append(f"  ├── Indicator: {ind}")
            related = [e for e in evidence_items if e.indicator_name == ind]
            for i, ev in enumerate(related):
                prefix = "  │   └──" if i == len(related) - 1 else "  │   ├──"
                masked_val = cls._mask_value(ev.observed_field, str(ev.observed_value))
                lines.append(
                    f"{prefix} Evidence: {ev.evidence_id[:8]}… "
                    f"[{ev.source_type}.{ev.source_id}] "
                    f"{ev.observed_field}={masked_val}"
                )
        return "\n".join(lines)

    @classmethod
    def format_list_for_pdf(cls, items: List[EvidenceItem]) -> List[dict]:
        """
        Returns a list of dicts suitable for PDF table rendering.
        All values are PII-masked strings.
        """
        rows = []
        for item in items:
            masked_value = cls._mask_value(item.observed_field, str(item.observed_value))
            rows.append({
                "id":          item.evidence_id[:8] + "…",
                "source":      f"{item.source_type}\n{item.source_id}",
                "field":       item.observed_field,
                "value":       masked_value,
                "class":       item.classification.value,
                "confidence":  f"{item.confidence:.2f}",
                "description": item.description[:120],
            })
        return rows
