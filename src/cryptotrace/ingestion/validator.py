"""
Schema validation utilities for data ingestion.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json


@dataclass
class IngestionReport:
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "duplicate_rows": self.duplicate_rows,
            "success_rate": (self.valid_rows / self.total_rows * 100) if self.total_rows > 0 else 0.0,
        }


def parse_list_field(val: Any) -> List[Any]:
    """Safely parse list fields from JSON string, delimiters, or native lists."""
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return []
        if val.startswith("[") and val.endswith("]"):
            try:
                return json.loads(val)
            except Exception:
                inner = val[1:-1].strip()
                return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
        elif ";" in val:
            return [x.strip() for x in val.split(";") if x.strip()]
        elif "," in val:
            return [x.strip() for x in val.split(",") if x.strip()]
        return [val]
    return [val]


def validate_record(record: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate a single raw transaction dictionary."""
    txid = record.get("txid")
    if not txid or not str(txid).strip():
        return False, "Missing or empty txid"
    if not record.get("timestamp"):
        return False, f"Missing timestamp in txid {txid}"
    return True, None
