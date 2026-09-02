"""
JSON and JSONL ingestion parser for CryptoTrace AI.
"""

import json
import pandas as pd
from typing import Tuple, List, Dict, Any
from src.cryptotrace.ingestion.validator import IngestionReport, validate_record, parse_list_field
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def load_json(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """Parse JSON/JSONL transaction records into canonical pandas DataFrame."""
    report = IngestionReport()
    records: List[Dict[str, Any]] = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                records = json.loads(content)
            else:
                for line in content.splitlines():
                    if line.strip():
                        records.append(json.loads(line))
    except Exception as e:
        report.errors.append(f"Failed to read JSON: {str(e)}")
        return pd.DataFrame(), report

    report.total_rows = len(records)
    valid = []
    seen = set()

    for idx, rec in enumerate(records):
        txid = str(rec.get("txid", "")).strip()
        if txid in seen:
            report.duplicate_rows += 1
            continue

        is_valid, err = validate_record(rec)
        if not is_valid:
            report.invalid_rows += 1
            continue

        rec["input_addresses"] = parse_list_field(rec.get("input_addresses", []))
        rec["output_addresses"] = parse_list_field(rec.get("output_addresses", []))
        rec["input_amounts"] = [
            float(x) for x in parse_list_field(rec.get("input_amounts", [0.0])) if str(x).replace(".", "", 1).isdigit()
        ] or [0.0]
        rec["output_amounts"] = [
            float(x) for x in parse_list_field(rec.get("output_amounts", [0.0])) if str(x).replace(".", "", 1).isdigit()
        ] or [0.0]
        rec["fee"] = float(rec.get("fee", 0.0))
        rec["label"] = int(rec.get("label", 2))

        seen.add(txid)
        valid.append(rec)
        report.valid_rows += 1

    return pd.DataFrame(valid), report
