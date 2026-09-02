"""
JSON ingestion parser for CryptoTrace AI transaction metadata.
"""

import json
import pandas as pd
from typing import Tuple, Dict, Any, List
import logging
from src.ingestion.canonical_schema import IngestionReport, validate_transaction_record, parse_list_field

logger = logging.getLogger(__name__)


def parse_json(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """
    Parse a JSON file (either JSON Array or Line-delimited JSON) of transactions.
    Gracefully handles malformed entries and normalizes to canonical DataFrame.
    """
    report = IngestionReport()
    records: List[Dict[str, Any]] = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                raw_data = json.loads(content)
                if isinstance(raw_data, list):
                    records = raw_data
            else:
                # Try reading line by line (JSONL)
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except Exception:
                            report.invalid_rows += 1
    except Exception as e:
        report.errors.append(f"Failed to read JSON file: {str(e)}")
        return pd.DataFrame(), report

    report.total_rows = len(records) + report.invalid_rows
    valid_records = []
    seen_txids = set()

    for idx, rec in enumerate(records):
        txid = str(rec.get("txid", "")).strip()
        if txid in seen_txids:
            report.duplicate_rows += 1
            continue

        is_valid, err = validate_transaction_record(rec)
        if not is_valid:
            report.invalid_rows += 1
            if len(report.errors) < 20:
                report.errors.append(f"Record {idx}: {err}")
            continue

        rec["input_addresses"] = parse_list_field(rec.get("input_addresses", []))
        rec["output_addresses"] = parse_list_field(rec.get("output_addresses", []))
        rec["input_amounts"] = [
            float(x)
            for x in parse_list_field(rec.get("input_amounts", [0.0]))
            if str(x).replace(".", "", 1).isdigit()
            or (str(x).startswith("-") and str(x)[1:].replace(".", "", 1).isdigit())
        ] or [0.0]
        rec["output_amounts"] = [
            float(x)
            for x in parse_list_field(rec.get("output_amounts", [0.0]))
            if str(x).replace(".", "", 1).isdigit()
            or (str(x).startswith("-") and str(x)[1:].replace(".", "", 1).isdigit())
        ] or [0.0]

        try:
            rec["fee"] = float(rec.get("fee", 0.0))
        except (ValueError, TypeError):
            rec["fee"] = 0.0

        try:
            rec["src_port"] = int(rec.get("src_port", 0))
            rec["dst_port"] = int(rec.get("dst_port", 0))
        except (ValueError, TypeError):
            rec["src_port"] = 0
            rec["dst_port"] = 0

        try:
            rec["label"] = int(rec.get("label", 2))
        except (ValueError, TypeError):
            rec["label"] = 2

        seen_txids.add(txid)
        valid_records.append(rec)
        report.valid_rows += 1

    df_clean = pd.DataFrame(valid_records)
    logger.info(f"Ingested JSON {filepath}: {report.valid_rows}/{report.total_rows} valid rows")
    return df_clean, report
