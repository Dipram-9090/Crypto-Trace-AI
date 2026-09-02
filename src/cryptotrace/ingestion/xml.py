"""
XML ingestion parser for CryptoTrace AI.
"""
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Tuple, Dict, Any, List
from src.cryptotrace.ingestion.validator import IngestionReport, validate_record, parse_list_field
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def load_xml(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """Parse XML transaction elements into canonical pandas DataFrame."""
    report = IngestionReport()
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        report.errors.append(f"Failed to parse XML: {str(e)}")
        return pd.DataFrame(), report

    tx_elements = root.findall(".//transaction") or root.findall(".//item") or [root]
    report.total_rows = len(tx_elements)
    valid = []
    seen = set()

    for idx, elem in enumerate(tx_elements):
        rec: Dict[str, Any] = {c.tag.lower(): c.text.strip() if c.text else "" for c in elem}
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
        rec["input_amounts"] = [float(x) for x in parse_list_field(rec.get("input_amounts", [0.0])) if str(x).replace('.','',1).isdigit()] or [0.0]
        rec["output_amounts"] = [float(x) for x in parse_list_field(rec.get("output_amounts", [0.0])) if str(x).replace('.','',1).isdigit()] or [0.0]
        rec["fee"] = float(rec.get("fee", 0.0))
        rec["label"] = int(rec.get("label", 2))

        seen.add(txid)
        valid.append(rec)
        report.valid_rows += 1

    return pd.DataFrame(valid), report
