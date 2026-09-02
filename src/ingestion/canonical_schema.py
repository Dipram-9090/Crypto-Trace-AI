"""
Canonical schema definitions and validation utilities for CryptoTrace AI data ingestion.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime


REQUIRED_COLUMNS = [
    "txid",
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "input_addresses",
    "output_addresses",
    "input_amounts",
    "output_amounts",
    "fee",
    "script_type",
    "src_country",
    "dst_country",
    "src_asn",
    "dst_asn",
    "label",
    "entity_type"
]

IP_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")


@dataclass
class IngestionReport:
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    missing_fields_count: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "duplicate_rows": self.duplicate_rows,
            "missing_fields_count": self.missing_fields_count,
            "error_sample": self.errors[:10],
            "success_rate": (self.valid_rows / self.total_rows * 100) if self.total_rows > 0 else 0.0
        }


def parse_list_field(val: Any) -> List[Any]:
    """Safely parse list fields from strings, JSON, or Python objects."""
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
                # Fallback to comma separated inside brackets
                inner = val[1:-1].strip()
                if not inner:
                    return []
                return [x.strip().strip("'\"") for x in inner.split(",")]
        elif ";" in val:
            return [x.strip() for x in val.split(";") if x.strip()]
        elif "," in val:
            return [x.strip() for x in val.split(",") if x.strip()]
        else:
            return [val]
    return [val]


def validate_transaction_record(record: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate a single transaction dictionary against canonical schema rules."""
    txid = record.get("txid")
    if not txid or not str(txid).strip():
        return False, "Missing or empty txid"

    # Validate timestamp
    ts = record.get("timestamp")
    if ts is None or str(ts).strip() == "":
        return False, f"Missing timestamp in txid {txid}"

    # Validate amounts and addresses
    inputs = parse_list_field(record.get("input_addresses", []))
    outputs = parse_list_field(record.get("output_addresses", []))
    if not inputs and not outputs:
        return False, f"Both input and output addresses are empty in txid {txid}"

    # Validate ports
    try:
        src_p = int(record.get("src_port", 0))
        dst_p = int(record.get("dst_port", 0))
        if not (0 <= src_p <= 65535 and 0 <= dst_p <= 65535):
            return False, f"Invalid port range in txid {txid}"
    except (ValueError, TypeError):
        return False, f"Port values cannot be parsed to integer in txid {txid}"

    return True, None
