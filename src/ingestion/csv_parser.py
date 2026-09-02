"""
CSV ingestion parser for CryptoTrace AI transaction metadata.
"""
import pandas as pd
from typing import Tuple, Dict, Any
import logging
from src.ingestion.canonical_schema import (
    IngestionReport,
    validate_transaction_record,
    parse_list_field
)

logger = logging.getLogger(__name__)


def parse_csv(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """
    Parse a CSV file of transaction records into canonical pandas DataFrame.
    Gracefully handles malformed rows, duplicate transactions, and type conversions.
    """
    report = IngestionReport()
    try:
        df_raw = pd.read_csv(filepath, dtype=str)
    except Exception as e:
        report.errors.append(f"Failed to read CSV file: {str(e)}")
        return pd.DataFrame(), report

    report.total_rows = len(df_raw)
    valid_records = []
    seen_txids = set()

    for idx, row in df_raw.iterrows():
        rec = row.to_dict()
        txid = str(rec.get("txid", "")).strip()

        if txid in seen_txids:
            report.duplicate_rows += 1
            continue

        is_valid, err = validate_transaction_record(rec)
        if not is_valid:
            report.invalid_rows += 1
            if len(report.errors) < 20:
                report.errors.append(f"Row {idx}: {err}")
            continue

        # Parse list fields
        rec["input_addresses"] = parse_list_field(rec.get("input_addresses", []))
        rec["output_addresses"] = parse_list_field(rec.get("output_addresses", []))
        rec["input_amounts"] = [float(x) for x in parse_list_field(rec.get("input_amounts", [0.0])) if str(x).replace('.', '', 1).isdigit() or (str(x).startswith('-') and str(x)[1:].replace('.', '', 1).isdigit())] or [0.0]
        rec["output_amounts"] = [float(x) for x in parse_list_field(rec.get("output_amounts", [0.0])) if str(x).replace('.', '', 1).isdigit() or (str(x).startswith('-') and str(x)[1:].replace('.', '', 1).isdigit())] or [0.0]

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

        # Label: 0=licit, 1=illicit, 2=unknown / other
        try:
            rec["label"] = int(rec.get("label", 2))
        except (ValueError, TypeError):
            rec["label"] = 2

        seen_txids.add(txid)
        valid_records.append(rec)
        report.valid_rows += 1

    df_clean = pd.DataFrame(valid_records)
    logger.info(f"Ingested CSV {filepath}: {report.valid_rows}/{report.total_rows} valid rows")
    return df_clean, report
