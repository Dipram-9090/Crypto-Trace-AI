"""
Wallet-level historical and behavioral feature tracking for CryptoTrace AI.
Tracks dynamic state strictly without future information leakage.
"""
from collections import defaultdict
from typing import Dict, Any, List
import numpy as np


class WalletTracker:
    """
    Maintains historical state per wallet address up to current transaction timestamp.
    """
    def __init__(self):
        self.wallet_tx_count = defaultdict(int)
        self.wallet_sent_count = defaultdict(int)
        self.wallet_recv_count = defaultdict(int)
        self.wallet_sent_amounts = defaultdict(list)
        self.wallet_recv_amounts = defaultdict(list)
        self.wallet_ips = defaultdict(set)
        self.wallet_asns = defaultdict(set)

    def extract_and_update(self, row: Dict[str, Any]) -> Dict[str, float]:
        inputs = row.get("input_addresses", [])
        outputs = row.get("output_addresses", [])
        in_amounts = row.get("input_amounts", [0.0])
        out_amounts = row.get("output_amounts", [0.0])
        src_ip = str(row.get("src_ip", ""))
        src_asn = str(row.get("src_asn", ""))

        primary_wallet = inputs[0] if inputs else (outputs[0] if outputs else "UNKNOWN")

        # Snapshot metrics before updating with current tx (prevent leakage)
        prior_tx_count = self.wallet_tx_count[primary_wallet]
        prior_sent = self.wallet_sent_count[primary_wallet]
        prior_recv = self.wallet_recv_count[primary_wallet]
        prior_ips = len(self.wallet_ips[primary_wallet])
        prior_asns = len(self.wallet_asns[primary_wallet])

        hist_sent = self.wallet_sent_amounts[primary_wallet]
        avg_sent = float(np.mean(hist_sent)) if hist_sent else 0.0
        std_sent = float(np.std(hist_sent)) if len(hist_sent) > 1 else 0.0

        hist_recv = self.wallet_recv_amounts[primary_wallet]
        avg_recv = float(np.mean(hist_recv)) if hist_recv else 0.0

        # Update historical state with current transaction
        for idx, w in enumerate(inputs):
            self.wallet_tx_count[w] += 1
            self.wallet_sent_count[w] += 1
            amt = in_amounts[idx] if idx < len(in_amounts) else 0.0
            self.wallet_sent_amounts[w].append(amt)
            if src_ip:
                self.wallet_ips[w].add(src_ip)
            if src_asn:
                self.wallet_asns[w].add(src_asn)

        for idx, w in enumerate(outputs):
            self.wallet_tx_count[w] += 1
            self.wallet_recv_count[w] += 1
            amt = out_amounts[idx] if idx < len(out_amounts) else 0.0
            self.wallet_recv_amounts[w].append(amt)

        return {
            "wallet_prior_tx_count": float(prior_tx_count),
            "wallet_prior_sent_count": float(prior_sent),
            "wallet_prior_recv_count": float(prior_recv),
            "wallet_unique_ips_count": float(prior_ips),
            "wallet_unique_asns_count": float(prior_asns),
            "wallet_avg_sent_amount": avg_sent,
            "wallet_std_sent_amount": std_sent,
            "wallet_avg_recv_amount": avg_recv,
            "wallet_in_out_tx_ratio": (prior_recv / prior_sent) if prior_sent > 0 else float(prior_recv)
        }
