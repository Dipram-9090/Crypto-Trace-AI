"""UTXO and Account-Based Model Normalizer."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class UTXONormalizer:
    """Normalizes Bitcoin UTXO structures (multiple inputs/outputs) into edge-list formats."""

    @staticmethod
    def flatten_utxo_transaction(tx_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Converts multi-input multi-output UTXO transaction to directed graph flow edges."""
        tx_hash = tx_dict.get("tx_hash", "unknown")
        timestamp = tx_dict.get("timestamp", None)
        inputs = tx_dict.get("inputs", [])
        outputs = tx_dict.get("outputs", [])
        fee = tx_dict.get("fee", 0.0)

        total_in = sum(inp.get("value", 0.0) for inp in inputs) or 1.0
        total_out = sum(out.get("value", 0.0) for out in outputs) or 1.0

        edges = []
        for inp in inputs:
            sender = inp.get("address", "coinbase")
            in_val = inp.get("value", 0.0)
            in_weight = in_val / total_in

            for out in outputs:
                receiver = out.get("address", "unknown")
                out_val = out.get("value", 0.0)
                # Apportion output value proportionally based on input weight
                apportioned_amount = out_val * in_weight

                edges.append({
                    "tx_hash": tx_hash,
                    "timestamp": timestamp,
                    "sender": sender,
                    "receiver": receiver,
                    "amount": apportioned_amount,
                    "fee": fee * in_weight,
                    "chain": "bitcoin",
                    "type": "utxo_transfer"
                })

        return edges

    @staticmethod
    def normalize_batch(utxo_txs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Batch processes list of UTXO dicts into flattened pandas DataFrame."""
        all_edges = []
        for tx in utxo_txs:
            all_edges.extend(UTXONormalizer.flatten_utxo_transaction(tx))
        return pd.DataFrame(all_edges)
