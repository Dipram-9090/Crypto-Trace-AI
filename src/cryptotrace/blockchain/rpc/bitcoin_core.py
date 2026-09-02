"""
Optional Bitcoin Core JSON-RPC Adapter (Offline-Safe).
"""

from typing import Optional, Dict, Any
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BitcoinCoreRPC:
    """Optional offline-safe Bitcoin Core JSON-RPC client adapter."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8332, user: str = "", password: str = ""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.is_connected = False

    def check_connection(self) -> bool:
        """Offline-safe connectivity check."""
        return False

    def get_raw_transaction(self, txid: str) -> Optional[Dict[str, Any]]:
        """Fetch raw transaction JSON if connected, else return None."""
        if not self.is_connected:
            return None
        return None
