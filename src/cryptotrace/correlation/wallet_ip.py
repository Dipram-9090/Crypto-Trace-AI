"""
Wallet Address to Infrastructure IP Correlation.
"""

from collections import defaultdict
from typing import Dict, List, Set


class WalletIPCorrelator:
    """Discovers shared infrastructure and address hopping across network IPs."""

    def __init__(self):
        self.wallet_to_ips = defaultdict(set)
        self.ip_to_wallets = defaultdict(set)

    def correlate(self, wallet: str, ip: str):
        if wallet and ip:
            self.wallet_to_ips[wallet].add(ip)
            self.ip_to_wallets[ip].add(wallet)

    def get_shared_infrastructure_index(self, ip: str) -> float:
        """Returns normalized score based on distinct wallets collocated on this IP."""
        cnt = len(self.ip_to_wallets.get(ip, []))
        return min(1.0, cnt / 10.0)

    def get_wallet_ip_diversity(self, wallet: str) -> int:
        """Count of distinct IP addresses used by wallet."""
        return len(self.wallet_to_ips.get(wallet, []))
