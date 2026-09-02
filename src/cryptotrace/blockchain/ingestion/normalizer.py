"""
Schema Normalization and Validation Engine for Heterogeneous Blockchain Datasets.
Automatically detects column variations (e.g., hash vs txid, sender vs input_address)
and converts any dataset into strongly typed, canonical BitcoinTransaction objects.
"""

import json
import math
from typing import Dict, Any, List, Tuple, Optional, Set
import pandas as pd
from datetime import datetime
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput
from src.cryptotrace.blockchain.addresses.validator import is_valid_bitcoin_address
from src.cryptotrace.blockchain.addresses.classifier import classify_address_encoding
from src.cryptotrace.blockchain.bitcoin.scripts import identify_script_type
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)

# Aliases for automatic field mapping
FIELD_ALIASES: Dict[str, List[str]] = {
    "txid": ["txid", "transaction_id", "hash", "tx_hash", "id", "tx_id", "transactionHash"],
    "input_addresses": [
        "input_addresses", "input_address", "inputs", "from_address", "from_addresses",
        "sender", "senders", "src_addr", "from", "source", "vin"
    ],
    "output_addresses": [
        "output_addresses", "output_address", "outputs", "to_address", "to_addresses",
        "receiver", "receivers", "dst_addr", "to", "destination", "vout"
    ],
    "input_amounts": ["input_amounts", "input_amount", "in_amounts", "in_amount"],
    "output_amounts": ["output_amounts", "output_amount", "out_amounts", "out_amount", "amount", "value", "btc_amount", "values"],
    "fee": ["fee", "transaction_fee", "tx_fee", "fees", "network_fee"],
    "timestamp": ["timestamp", "time", "block_time", "date", "datetime", "created_at", "block_timestamp"],
    "block_height": ["block_height", "height", "block_number", "block", "blockNumber"],
    "block_hash": ["block_hash", "blockhash", "blockHash"],
    "locktime": ["locktime", "lock_time"],
    "version": ["version", "tx_version"],
    "script_type": ["script_type", "type", "script", "encoding"],
}


class DatasetValidationReport:
    """Detailed forensic quality and schema detection report."""

    def __init__(self, dataset_id: str = "dataset_default"):
        self.dataset_id = dataset_id
        self.detected_schema: Dict[str, str] = {}
        self.total_records: int = 0
        self.valid_records: int = 0
        self.invalid_records: int = 0
        self.duplicate_records: int = 0
        self.missing_mandatory_fields: List[str] = []
        self.unsupported_fields: List[str] = []
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "detected_schema": self.detected_schema,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "duplicate_records": self.duplicate_records,
            "missing_mandatory_fields": self.missing_mandatory_fields,
            "unsupported_fields": self.unsupported_fields,
            "errors": self.errors[:50],  # cap error samples
        }


def detect_schema_mapping(columns: List[str]) -> Dict[str, str]:
    """Map detected columns in raw dataset to canonical internal fields."""
    mapping: Dict[str, str] = {}
    lower_cols = {col.lower().strip(): col for col in columns}

    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_cols:
                mapping[canonical] = lower_cols[alias.lower()]
                break
    return mapping


import ast


def _parse_list_or_scalar(val: Any) -> List[Any]:
    """Safely convert strings, JSON strings, Python literal lists, or single items to Python list."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return []
    if isinstance(val, (list, tuple, set)):
        return list(val)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return []
        if val.startswith("[") and val.endswith("]"):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, (list, tuple)):
                    return list(parsed)
            except Exception:
                pass
        if "," in val:
            return [x.strip() for x in val.split(",") if x.strip()]
        return [val]
    return [val]


def _parse_float(val: Any, default: float = 0.0) -> float:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return default


def normalize_record_to_transaction(
    row: Dict[str, Any],
    mapping: Dict[str, str],
    dataset_id: Optional[str] = None,
) -> Optional[BitcoinTransaction]:
    """Convert an arbitrary dict row into a canonical BitcoinTransaction object."""
    # Extract txid
    txid_col = mapping.get("txid")
    txid = str(row.get(txid_col, "")).strip() if txid_col else ""
    if not txid:
        # Check if hash or id exists
        txid = str(row.get("txid") or row.get("hash") or row.get("id") or "").strip()
    if not txid or txid == "nan":
        return None

    # Timestamp
    ts_col = mapping.get("timestamp")
    raw_ts = row.get(ts_col) if ts_col else (row.get("timestamp") or row.get("time") or datetime.utcnow().isoformat())
    timestamp_str = str(raw_ts).strip()

    # Block info
    bh_col = mapping.get("block_height")
    block_height = int(_parse_float(row.get(bh_col), 0)) if bh_col and row.get(bh_col) is not None else None
    
    bhash_col = mapping.get("block_hash")
    block_hash = str(row.get(bhash_col, "")).strip() if bhash_col else None

    # Fee
    fee_col = mapping.get("fee")
    fee = _parse_float(row.get(fee_col), 0.0) if fee_col else 0.0

    # Inputs
    in_addr_col = mapping.get("input_addresses")
    in_amt_col = mapping.get("input_amounts")
    raw_in_addrs = _parse_list_or_scalar(row.get(in_addr_col)) if in_addr_col else []
    raw_in_amts = _parse_list_or_scalar(row.get(in_amt_col)) if in_amt_col else []

    inputs: List[TxInput] = []
    for idx, addr in enumerate(raw_in_addrs):
        if not addr:
            continue
        amt = _parse_float(raw_in_amts[idx]) if idx < len(raw_in_amts) else 0.0
        script_t = classify_address_encoding(str(addr))
        inputs.append(
            TxInput(
                prev_txid=f"prev_{txid[:8]}_{idx}",
                vout=idx,
                address=str(addr).strip(),
                amount=amt,
                script_type=script_t,
            )
        )

    # Outputs
    out_addr_col = mapping.get("output_addresses")
    out_amt_col = mapping.get("output_amounts")
    raw_out_addrs = _parse_list_or_scalar(row.get(out_addr_col)) if out_addr_col else []
    raw_out_amts = _parse_list_or_scalar(row.get(out_amt_col)) if out_amt_col else []

    # If output_amounts was mapped to single amount column and out_addrs is list
    if len(raw_out_amts) == 1 and len(raw_out_addrs) > 1:
        # Split or replicate
        raw_out_amts = [_parse_float(raw_out_amts[0]) / len(raw_out_addrs)] * len(raw_out_addrs)

    outputs: List[TxOutput] = []
    for idx, addr in enumerate(raw_out_addrs):
        if not addr:
            continue
        amt = _parse_float(raw_out_amts[idx]) if idx < len(raw_out_amts) else 0.0
        stype = classify_address_encoding(str(addr))
        outputs.append(
            TxOutput(
                address=str(addr).strip(),
                amount=amt,
                vout=idx,
                script_type=stype,
            )
        )

    # Calculate fee if 0 and inputs/outputs have valid sums
    total_in = sum(i.amount for i in inputs)
    total_out = sum(o.amount for o in outputs)
    if fee == 0.0 and total_in > total_out and total_out > 0:
        fee = round(total_in - total_out, 8)

    # Approximate size/vsize
    vsize = 10 + len(inputs) * 68 + len(outputs) * 31

    return BitcoinTransaction(
        txid=txid,
        version=int(_parse_float(row.get("version"), 2)),
        locktime=int(_parse_float(row.get("locktime"), 0)),
        inputs=inputs,
        outputs=outputs,
        fee=fee,
        fee_rate=round((fee * 1e8) / max(1, vsize), 2) if fee > 0 else 0.0,
        timestamp=timestamp_str,
        block_height=block_height,
        block_hash=block_hash,
        vsize=vsize,
        size=vsize,
        dataset_id=dataset_id,
    )


class TransactionNormalizer:
    """Comprehensive normalization service with dataset isolation and reporting."""

    def __init__(self, dataset_id: str = "dataset_default"):
        self.dataset_id = dataset_id

    def normalize_dataframe(
        self, df: pd.DataFrame
    ) -> Tuple[List[BitcoinTransaction], DatasetValidationReport]:
        report = DatasetValidationReport(dataset_id=self.dataset_id)
        report.total_records = len(df)

        if df.empty:
            report.missing_mandatory_fields = ["txid", "input_addresses", "output_addresses"]
            return [], report

        mapping = detect_schema_mapping(list(df.columns))
        report.detected_schema = mapping

        # Check mandatory fields
        if "txid" not in mapping:
            report.missing_mandatory_fields.append("txid")
        if "input_addresses" not in mapping and "output_addresses" not in mapping:
            report.missing_mandatory_fields.append("addresses")

        report.unsupported_fields = [c for c in df.columns if c not in mapping.values()]

        seen_txids: Set[str] = set()
        transactions: List[BitcoinTransaction] = []

        for idx, row in df.iterrows():
            r_dict = row.to_dict()
            tx = normalize_record_to_transaction(r_dict, mapping, dataset_id=self.dataset_id)
            if not tx:
                report.invalid_records += 1
                report.errors.append(f"Row {idx}: missing required txid")
                continue

            if tx.txid in seen_txids:
                report.duplicate_records += 1
                continue

            seen_txids.add(tx.txid)
            transactions.append(tx)
            report.valid_records += 1

        return transactions, report
