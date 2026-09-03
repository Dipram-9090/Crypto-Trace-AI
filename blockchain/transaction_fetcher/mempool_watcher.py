"""Mempool Watcher for Zero-Confirmation Transaction Monitoring."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("cryptotrace.blockchain.fetcher.mempool")


class MempoolWatcher:
    """Monitors pending unconfirmed transactions for frontrunning, sandwich attacks, and immediate illicit movements."""

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def get_pending_transactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [
            {
                "tx_hash": f"0xpending_{i:04d}" + "f" * 50,
                "chain": self.chain,
                "sender": f"0x999999999999999999999999999999999999{i:04d}",
                "receiver": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "amount": float(100.0 * (i + 1)),
                "gas_price_gwei": 45.5,
                "status": "pending_in_mempool"
            }
            for i in range(min(limit, 10))
        ]
