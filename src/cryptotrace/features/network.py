"""
Network-layer metadata and IP infrastructure correlation features.
"""

from collections import defaultdict
from typing import Dict, Any


class NetworkTracker:
    """Tracks network metadata and colocation across IPs and ports."""

    def __init__(self):
        self.ip_tx_count = defaultdict(int)
        self.ip_wallets = defaultdict(set)
        self.ip_ports = defaultdict(set)

    def extract_and_update(self, row: Dict[str, Any]) -> Dict[str, float]:
        src_ip = str(row.get("src_ip", ""))
        src_port = int(row.get("src_port", 0))
        dst_port = int(row.get("dst_port", 8333))
        inputs = row.get("input_addresses", [])

        prior_ip_txs = self.ip_tx_count[src_ip]
        prior_ip_wallets = len(self.ip_wallets[src_ip])
        prior_ip_ports = len(self.ip_ports[src_ip])

        is_std_btc_port = 1.0 if (dst_port == 8333 or src_port == 8333) else 0.0
        is_ephemeral_port = 1.0 if src_port > 1024 else 0.0

        if src_ip:
            self.ip_tx_count[src_ip] += 1
            for w in inputs:
                self.ip_wallets[src_ip].add(w)
            self.ip_ports[src_ip].add(src_port)

        shared_infra_score = float(min(1.0, prior_ip_wallets / 10.0))

        return {
            "ip_prior_tx_count": float(prior_ip_txs),
            "ip_associated_wallets_count": float(prior_ip_wallets),
            "ip_unique_ports_used": float(prior_ip_ports),
            "is_standard_btc_port": is_std_btc_port,
            "is_ephemeral_src_port": is_ephemeral_port,
            "shared_infrastructure_indicator": shared_infra_score,
        }
