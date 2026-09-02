"""
XML ingestion parser for CryptoTrace AI transaction metadata.
"""

import xml.etree.ElementTree as ET
import pandas as pd
from typing import Tuple, Dict, Any, List
import logging
from src.ingestion.canonical_schema import IngestionReport, validate_transaction_record, parse_list_field

logger = logging.getLogger(__name__)


def parse_xml(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """
    Parse an XML file of transaction elements into a canonical DataFrame.
    """
    report = IngestionReport()
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        report.errors.append(f"Failed to parse XML file: {str(e)}")
        return pd.DataFrame(), report

    # Find all transaction elements (support <transaction>, <item>, <record>, <tx>)
    tx_elements = []
    for tag in ["transaction", "item", "record", "tx"]:
        elems = root.findall(f".//{tag}")
        if elems:
            tx_elements = elems
            break
    if not tx_elements and root.tag in ["transaction", "item", "record", "tx"]:
        tx_elements = [root]

    report.total_rows = len(tx_elements)
    valid_records = []
    seen_txids = set()

    for idx, elem in enumerate(tx_elements):
        rec: Dict[str, Any] = {}
        for child in elem:
            tag = child.tag.lower()
            text = child.text.strip() if child.text else ""
            rec[tag] = text

        txid = str(rec.get("txid", "")).strip()
        if txid in seen_txids:
            report.duplicate_rows += 1
            continue

        is_valid, err = validate_transaction_record(rec)
        if not is_valid:
            report.invalid_rows += 1
            if len(report.errors) < 20:
                report.errors.append(f"Element {idx}: {err}")
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
    logger.info(f"Ingested XML {filepath}: {report.valid_rows}/{report.total_rows} valid rows")
    return df_clean, report
