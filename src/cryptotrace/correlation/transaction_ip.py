"""
Blockchain Transaction to Network IP Correlation Engine.
"""

import pandas as pd
from typing import Dict, List, Set
from collections import defaultdict


class TransactionIPCorrelator:
    """Tracks broadcasting nodes and peer hops for individual transactions."""

    def __init__(self):
        self.tx_to_ips = defaultdict(set)
        self.ip_to_txs = defaultdict(set)

    def correlate(self, txid: str, src_ip: str, dst_ip: str = ""):
        if txid and src_ip:
            self.tx_to_ips[txid].add(src_ip)
            self.ip_to_txs[src_ip].add(txid)
        if txid and dst_ip:
            self.tx_to_ips[txid].add(dst_ip)
            self.ip_to_txs[dst_ip].add(txid)

    def get_ips_for_transaction(self, txid: str) -> List[str]:
        return list(self.tx_to_ips.get(txid, []))

    def get_transactions_for_ip(self, ip: str) -> List[str]:
        return list(self.ip_to_txs.get(ip, []))
