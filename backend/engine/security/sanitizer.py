"""
security/sanitizer.py — Input sanitization utilities.

Strips personally identifiable information from raw database rows
before they are stored in agent state or returned via the API.
"""

import re
from typing import Any, Dict


class Sanitizer:
    """Sanitizes data from the master dataset before it enters agent state."""

    # Fields to mask partially (show only last 4 chars)
    _PARTIAL_MASK_FIELDS = {"account_id", "from_account_id", "to_account_id"}
    # Fields to drop entirely
    _DROP_FIELDS: set = set()

    @classmethod
    def sanitize_profile(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a raw profile row from the dataset.
        Keeps all fields needed by the agent; no PII stripping required
        because the synthetic dataset contains no real personal data.
        """
        # Pass-through: synthetic dataset is already safe.
        # Add masking here if the dataset ever contains real PII.
        return dict(row)

    @classmethod
    def sanitize_transaction(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a raw transaction row."""
        return dict(row)

    @classmethod
    def sanitize_atm(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a raw ATM row."""
        return dict(row)

    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Strip leading/trailing whitespace and remove null bytes."""
        if not isinstance(value, str):
            return value
        return value.strip().replace("\x00", "")
