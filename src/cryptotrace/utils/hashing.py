"""
Cryptographic and Forensic Hashing Helpers.
"""
import hashlib


def sha256_hash(data: str) -> str:
    """Return SHA-256 hex digest of string input."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def double_sha256(data: bytes) -> bytes:
    """Standard Bitcoin double-SHA256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
