"""
evidence/deduplicator.py — Prevents duplicate evidence records.

Deduplication is hash-based: if two EvidenceItems share the same canonical hash,
the second is discarded and the existing evidence_id is reused.
"""

from typing import Dict, List, Tuple
from .models import EvidenceItem


class EvidenceDeduplicator:
    """
    Stateless deduplication helper.

    Usage:
        dedup = EvidenceDeduplicator()
        unique_items, reused_ids = dedup.deduplicate(new_items, existing_items)
    """

    @staticmethod
    def deduplicate(
        new_items: List[EvidenceItem],
        existing_items: List[EvidenceItem],
    ) -> Tuple[List[EvidenceItem], Dict[str, str]]:
        """
        Deduplicates new_items against existing_items by hash.

        Returns:
            (unique_items, reuse_map)
            - unique_items: items that are genuinely new (not duplicates)
            - reuse_map: {new_evidence_id → existing_evidence_id} for all duplicates found
        """
        # Build hash → evidence_id index from existing evidence
        existing_index: Dict[str, str] = {
            item.hash: item.evidence_id for item in existing_items
        }

        unique_items: List[EvidenceItem] = []
        reuse_map: Dict[str, str] = {}

        seen_hashes: Dict[str, str] = dict(existing_index)  # copy

        for item in new_items:
            if item.hash in seen_hashes:
                # Duplicate: reuse existing evidence_id
                reuse_map[item.evidence_id] = seen_hashes[item.hash]
            else:
                unique_items.append(item)
                seen_hashes[item.hash] = item.evidence_id

        return unique_items, reuse_map

    @staticmethod
    def resolve_ids(
        evidence_ids: List[str],
        reuse_map: Dict[str, str],
    ) -> List[str]:
        """
        Given a list of evidence IDs and a reuse_map, return the canonical
        (deduplicated) evidence IDs.
        """
        return [reuse_map.get(eid, eid) for eid in evidence_ids]
