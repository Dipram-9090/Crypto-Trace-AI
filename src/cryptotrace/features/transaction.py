"""
Transaction-level structural and amount features.
"""

import numpy as np
from typing import Dict, Any, List


def calculate_entropy(amounts: List[float]) -> float:
    """Calculate Shannon entropy over normalized amount distributions."""
    if not amounts or len(amounts) <= 1:
        return 0.0
    arr = np.array(amounts, dtype=float)
    total = np.sum(arr)
    if total <= 0:
        return 0.0
    probs = arr / total
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def extract_transaction_features(row: Dict[str, Any]) -> Dict[str, float]:
    """Extract structural transaction features from a single row dictionary."""
    inputs = row.get("input_addresses", [])
    outputs = row.get("output_addresses", [])
    in_amounts = row.get("input_amounts", [0.0])
    out_amounts = row.get("output_amounts", [0.0])
    fee = float(row.get("fee", 0.0))

    in_count = len(inputs) if isinstance(inputs, list) else 1
    out_count = len(outputs) if isinstance(outputs, list) else 1

    total_in = float(sum(in_amounts)) if in_amounts else 0.0
    total_out = float(sum(out_amounts)) if out_amounts else 0.0
    tx_value = max(total_in, total_out)

    fee_ratio = (fee / total_in) if total_in > 0 else 0.0
    in_out_ratio = (in_count / out_count) if out_count > 0 else float(in_count)
    amount_in_out_ratio = (total_in / total_out) if total_out > 0 else 1.0

    out_variance = float(np.var(out_amounts)) if len(out_amounts) > 1 else 0.0
    out_entropy = calculate_entropy(out_amounts)
    in_entropy = calculate_entropy(in_amounts)

    fan_out_ratio = float(out_count / (in_count + 1e-5))

    return {
        "input_count": float(in_count),
        "output_count": float(out_count),
        "total_input_amount": total_in,
        "total_output_amount": total_out,
        "transaction_value": tx_value,
        "fee": fee,
        "fee_ratio": fee_ratio,
        "input_output_ratio": in_out_ratio,
        "amount_in_out_ratio": amount_in_out_ratio,
        "fan_out_ratio": fan_out_ratio,
        "output_amount_variance": out_variance,
        "output_entropy": out_entropy,
        "input_entropy": in_entropy,
        "is_high_fanout": 1.0 if out_count >= 8 else 0.0,
        "is_high_fanin": 1.0 if in_count >= 6 else 0.0,
    }
