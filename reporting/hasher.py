"""
reporting/hasher.py — SHA-256 integrity hash for generated PDF reports.

Purpose: detect accidental post-generation modification of a PDF.
The hash is computed from the raw binary file content.

Tests (same file → same hash; modified file → different hash) are in tests/phase5/test_report_hasher.py.
"""

import hashlib
import os
from typing import Optional


class ReportHasher:
    """Computes and verifies SHA-256 hashes of generated PDF files."""

    BLOCK_SIZE = 65536  # 64 KiB — memory-efficient for large PDFs

    @classmethod
    def hash_file(cls, file_path: str) -> str:
        """
        Returns the SHA-256 hex digest of the binary file at file_path.
        Raises FileNotFoundError if the file does not exist.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Report file not found: {file_path}")

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                block = f.read(cls.BLOCK_SIZE)
                if not block:
                    break
                sha256.update(block)
        return sha256.hexdigest()

    @classmethod
    def verify(cls, file_path: str, expected_hash: str) -> bool:
        """
        Returns True if the file at file_path matches the expected SHA-256 hash.
        Returns False if the file has been modified or is missing.
        """
        try:
            actual = cls.hash_file(file_path)
            return actual == expected_hash
        except FileNotFoundError:
            return False

    @classmethod
    def is_valid_pdf(cls, file_path: str) -> bool:
        """
        Quick binary validation: checks that the file starts with the PDF magic bytes %PDF.
        Does not perform a full PDF structure parse.
        """
        try:
            with open(file_path, "rb") as f:
                header = f.read(4)
            return header == b"%PDF"
        except (FileNotFoundError, IOError):
            return False
