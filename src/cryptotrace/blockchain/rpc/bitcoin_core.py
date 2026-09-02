"""
Bitcoin Core JSON-RPC Client Adapter (Offline-Safe).
Configurable via environment variables: BITCOIN_RPC_HOST, BITCOIN_RPC_PORT, BITCOIN_RPC_USER, BITCOIN_RPC_PASSWORD.
Seamlessly falls back to offline mode when RPC daemon is unreachable.
"""

import os
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BitcoinCoreRPC:
    """Offline-safe Bitcoin Core JSON-RPC client adapter."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 2.0,
    ):
        self.host = host or os.environ.get("BITCOIN_RPC_HOST", "127.0.0.1")
        self.port = int(port or os.environ.get("BITCOIN_RPC_PORT", 8332))
        self.user = user or os.environ.get("BITCOIN_RPC_USER", "")
        self.password = password or os.environ.get("BITCOIN_RPC_PASSWORD", "")
        self.timeout = timeout
        self.url = f"http://{self.host}:{self.port}"
        self._is_enabled = os.environ.get("BITCOIN_RPC_ENABLED", "false").lower() in ["true", "1", "yes"]

    def _call(self, method: str, params: Optional[list] = None) -> Optional[Any]:
        """Execute a JSON-RPC request."""
        if not self._is_enabled and not self.user:
            return None

        payload = json.dumps({
            "jsonrpc": "1.0",
            "id": f"cryptotrace_{method}",
            "method": method,
            "params": params or [],
        }).encode("utf-8")

        auth = base64.b64encode(f"{self.user}:{self.password}".encode("utf-8")).decode("ascii")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        }

        req = urllib.request.Request(self.url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("error"):
                    logger.warning(f"RPC error for {method}: {data['error']}")
                    return None
                return data.get("result")
        except (urllib.error.URLError, TimeoutError, ConnectionRefusedError, OSError):
            return None
        except Exception as e:
            logger.debug(f"RPC call failed for {method}: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if local Bitcoin Core daemon is responsive."""
        res = self._call("getblockchaininfo")
        return res is not None

    def get_blockchain_info(self) -> Optional[Dict[str, Any]]:
        """Fetch blockchain status metadata."""
        return self._call("getblockchaininfo")

    def get_block_hash(self, height: int) -> Optional[str]:
        """Get block hash at specific height."""
        return self._call("getblockhash", [height])

    def get_block(self, block_hash: str, verbosity: int = 2) -> Optional[Dict[str, Any]]:
        """Fetch block data by hash."""
        return self._call("getblock", [block_hash, verbosity])

    def get_raw_transaction(self, txid: str, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """Fetch transaction by txid."""
        return self._call("getrawtransaction", [txid, verbose])

    def decode_raw_transaction(self, hex_string: str) -> Optional[Dict[str, Any]]:
        """Decode raw serialized transaction hex string."""
        return self._call("decoderawtransaction", [hex_string])
