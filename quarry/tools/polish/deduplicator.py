"""Deduplication engine for Polish tool."""

import hashlib
import json
from typing import Any, Literal


class Deduplicator:
    """
    Deduplicate records based on configurable strategies.

    Supports:
    - Hash-based deduplication using specified key fields
    - Keep-first or keep-last strategies
    - Full record hashing or field-based hashing
    """

    def __init__(
        self,
        key_fields: list[str] | None = None,
        strategy: Literal["first", "last"] = "first",
    ):
        """
        Initialize deduplicator.

        Args:
            key_fields: List of field names to use for deduplication.
                       If None, uses entire record.
            strategy: "first" to keep first occurrence, "last" to keep last
        """
        self.key_fields = key_fields
        self.strategy = strategy
        self.seen_hashes: set[str] = set()
        self.last_records: dict[str, dict[str, Any]] = {}
        self.processed_count = 0
        self.duplicate_count = 0

    def _compute_hash(self, record: dict[str, Any]) -> str:
        """
        Compute hash for a record.

        Args:
            record: Record dictionary

        Returns:
            SHA256 hash string
        """
        if self.key_fields:
            # Hash only specified fields
            key_data = {k: record.get(k) for k in self.key_fields}
        else:
            # Hash entire record (excluding _meta if present)
            key_data = {k: v for k, v in record.items() if k != "_meta"}

        # Create stable JSON representation
        json_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def is_duplicate(self, record: dict[str, Any]) -> bool:
        """
        Check if record is a duplicate.

        Args:
            record: Record dictionary

        Returns:
            True if duplicate (should skip), False if unique (should keep)
        """
        record_hash = self._compute_hash(record)
        self.processed_count += 1

        if self.strategy == "first":
            # Keep first, skip subsequent duplicates
            if record_hash in self.seen_hashes:
                self.duplicate_count += 1
                return True
            self.seen_hashes.add(record_hash)
            return False

        else:  # strategy == "last"
            # Store all records, will filter at end
            if record_hash in self.last_records:
                self.duplicate_count += 1
            self.last_records[record_hash] = record
            return False  # Don't skip during processing

    def get_unique_records(self) -> list[dict[str, Any]]:
        """
        Get deduplicated records (for 'last' strategy).

        Returns:
            List of unique records (last occurrence of each)
        """
        if self.strategy == "last":
            return list(self.last_records.values())
        else:
            raise ValueError("get_unique_records() only valid for 'last' strategy")

    def reset(self):
        """Reset deduplicator state."""
        self.seen_hashes.clear()
        self.last_records.clear()
        self.processed_count = 0
        self.duplicate_count = 0

    def get_stats(self) -> dict[str, int]:
        """
        Get deduplication statistics.

        Returns:
            Dictionary with counts for reporting
        """
        if self.strategy == "first":
            unique_count = len(self.seen_hashes)
        else:
            unique_count = len(self.last_records)

        return {
            "processed_count": self.processed_count,
            "unique_count": unique_count,
            "duplicate_count": self.duplicate_count,
        }
