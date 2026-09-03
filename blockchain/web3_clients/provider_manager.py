"""Multi-Chain Web3 Provider Manager (Ethereum, Polygon, BSC, Arbitrum, Optimism)."""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("cryptotrace.blockchain.web3_clients.provider")

DEFAULT_CHAIN_RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "polygon": "https://polygon-rpc.com",
    "bsc": "https://binance.llamarpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "optimism": "https://mainnet.optimism.io"
}


class ProviderManager:
    """Manages active RPC connections, failover, and rate limiting across EVM blockchains."""

    def __init__(self, custom_rpcs: Optional[Dict[str, str]] = None):
        self.rpcs = {**DEFAULT_CHAIN_RPCS, **(custom_rpcs or {})}
        self.active_connections = {}

    def get_rpc_url(self, chain: str) -> str:
        chain_key = chain.lower()
        return self.rpcs.get(chain_key, self.rpcs["ethereum"])

    def get_supported_chains(self) -> list:
        return list(self.rpcs.keys())
