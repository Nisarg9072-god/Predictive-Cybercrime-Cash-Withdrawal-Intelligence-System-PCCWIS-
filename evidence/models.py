"""
evidence/models.py — Structured Evidence Data Models

CLASSIFICATION HIERARCHY:
  OBSERVED   — directly read from a database field (ground truth from source record)
  DERIVED    — computed from one or more OBSERVED values (e.g., hop count from transactions)
  INFERRED   — conclusion drawn from DERIVED + OBSERVED evidence (e.g., "chain is layered")
  PREDICTED  — forward-looking projection (e.g., "likely to cashout in region X")
  SYNTHETIC  — generated from test fixtures; NEVER to be mixed with real evidence

INVARIANT: INFERRED and PREDICTED evidence must never be presented as OBSERVED.
           This is enforced by EvidenceValidator.
"""

import hashlib
import json
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, field_validator, model_validator


class EvidenceClassification(str, Enum):
    OBSERVED  = "OBSERVED"   # Direct source field read
    DERIVED   = "DERIVED"    # Computed from observed values
    INFERRED  = "INFERRED"   # Logical conclusion from evidence
    PREDICTED = "PREDICTED"  # Forward projection
    SYNTHETIC = "SYNTHETIC"  # Test fixture — never real evidence


class EvidenceItem(BaseModel):
    evidence_id:       str
    investigation_id:  str
    source_type:       str              # e.g. TRANSACTION, PROFILE, SCENARIO, ATM
    source_id:         str              # e.g. TXN_00001, CHAIN_001
    observed_field:    str              # e.g. is_laundering, hop_layer
    observed_value:    Any              # Raw observed value
    description:       str              # Human-readable description
    confidence:        float            # [0.0, 1.0]
    timestamp:         str              # ISO-8601 UTC
    hash:              str              # Canonical deterministic hash
    classification:    EvidenceClassification
    indicator_name:    Optional[str] = None   # Which indicator this supports
    parent_evidence_id: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {v}")
        return round(v, 4)

    @classmethod
    def compute_hash(cls, investigation_id: str,
                     source_type: str, source_id: str,
                     observed_field: str, observed_value: Any,
                     classification: str,
                     parent_evidence_id: Optional[str] = None) -> str:
        """
        Deterministic canonical hash. Same evidence always produces the same hash.
        Changing any content field produces a different hash.
        """
        canonical = json.dumps({
            "investigation_id": investigation_id,
            "source_type":     source_type,
            "source_id":       source_id,
            "observed_field":  observed_field,
            "observed_value":  str(observed_value),
            "classification":  classification,
            "parent_evidence_id": parent_evidence_id
        }, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def create(
        cls,
        evidence_id: str,
        investigation_id: str,
        source_type: str,
        source_id: str,
        observed_field: str,
        observed_value: Any,
        description: str,
        confidence: float,
        classification: EvidenceClassification,
        indicator_name: Optional[str] = None,
        parent_evidence_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> "EvidenceItem":
        ts = timestamp or datetime.now(UTC).isoformat()
        h  = cls.compute_hash(
            investigation_id, source_type, source_id,
            observed_field, observed_value, classification.value, parent_evidence_id
        )
        return cls(
            evidence_id=evidence_id,
            investigation_id=investigation_id,
            source_type=source_type,
            source_id=source_id,
            observed_field=observed_field,
            observed_value=observed_value,
            description=description,
            confidence=confidence,
            timestamp=ts,
            hash=h,
            classification=classification,
            indicator_name=indicator_name,
            parent_evidence_id=parent_evidence_id,
        )

    def to_db_dict(self) -> dict:
        """Serialise to flat dict for database storage."""
        return {
            "evidence_id":      self.evidence_id,
            "investigation_id": self.investigation_id,
            "source_type":      self.source_type,
            "source_id":        self.source_id,
            "observed_field":   self.observed_field,
            "observed_value":   str(self.observed_value),
            "description":      self.description,
            "confidence":       self.confidence,
            "timestamp":        self.timestamp,
            "hash":             self.hash,
            "classification":   self.classification.value,
            "indicator_name":   self.indicator_name or "",
            "parent_evidence_id": self.parent_evidence_id or "",
        }
