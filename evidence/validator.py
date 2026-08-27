"""
evidence/validator.py — Evidence classification integrity enforcement.

INVARIANT: INFERRED and PREDICTED evidence must never be presented as OBSERVED.
"""

from typing import List, Tuple
from .models import EvidenceClassification, EvidenceItem


class ValidationError(Exception):
    pass


class EvidenceValidator:
    """Validates EvidenceItem correctness before persistence or display."""

    REQUIRED_FIELDS = {
        "evidence_id", "investigation_id", "source_type", "source_id",
        "observed_field", "observed_value", "description", "confidence",
        "timestamp", "hash", "classification",
    }

    # These classifications must never be re-labelled as OBSERVED
    NON_OBSERVABLE = {EvidenceClassification.INFERRED, EvidenceClassification.PREDICTED}

    @classmethod
    def validate(cls, item: EvidenceItem) -> Tuple[bool, List[str]]:
        """
        Returns (is_valid, list_of_error_strings).
        Does not raise — allows batch validation.
        """
        errors: List[str] = []

        # 1. Required fields present
        d = item.model_dump()
        for field in cls.REQUIRED_FIELDS:
            if d.get(field) is None or d.get(field) == "":
                errors.append(f"Missing required field: {field}")

        # 2. Confidence range
        if not (0.0 <= item.confidence <= 1.0):
            errors.append(f"confidence={item.confidence} out of [0.0, 1.0]")

        # 3. Classification integrity — INFERRED/PREDICTED ≠ OBSERVED
        if item.classification in cls.NON_OBSERVABLE:
            # The field name must not claim it is directly observed
            if "direct" in item.description.lower() and "observ" in item.description.lower():
                errors.append(
                    f"Classification={item.classification.value} evidence must not claim "
                    f"to be directly observed. Revise description."
                )
            
            # Provenance rule: derived/inferred/predicted items should have a parent evidence
            if item.parent_evidence_id is None and item.classification != EvidenceClassification.SYNTHETIC:
                errors.append(
                    f"Classification={item.classification.value} evidence MUST have a parent_evidence_id "
                    f"tracing back to its observed source."
                )

        # 4. SYNTHETIC must not co-exist with OBSERVED in the same investigation
        # (This check is done at collection time in EvidenceDeduplicator, not per-item)

        # 5. Hash integrity
        expected = EvidenceItem.compute_hash(
            item.investigation_id, item.source_type,
            item.source_id, item.observed_field, item.observed_value,
            item.classification.value, item.parent_evidence_id
        )
        if item.hash != expected:
            errors.append(f"Hash mismatch: stored={item.hash[:12]}… expected={expected[:12]}…")

        return (len(errors) == 0), errors

    @classmethod
    def validate_batch(cls, items: List[EvidenceItem]) -> Tuple[bool, List[str]]:
        all_errors: List[str] = []
        classifications = {item.classification for item in items}

        # SYNTHETIC must never mix with OBSERVED/DERIVED/INFERRED
        if EvidenceClassification.SYNTHETIC in classifications:
            real_cls = classifications - {EvidenceClassification.SYNTHETIC}
            if real_cls:
                all_errors.append(
                    "SYNTHETIC evidence items must never be mixed with real "
                    f"({', '.join(c.value for c in real_cls)}) evidence."
                )

        for item in items:
            ok, errs = cls.validate(item)
            if not ok:
                all_errors.extend([f"[{item.evidence_id}] {e}" for e in errs])

        return (len(all_errors) == 0), all_errors

    @classmethod
    def assert_valid(cls, item: EvidenceItem) -> None:
        """Raises ValidationError if invalid."""
        ok, errors = cls.validate(item)
        if not ok:
            raise ValidationError(f"EvidenceItem {item.evidence_id} invalid: {errors}")
