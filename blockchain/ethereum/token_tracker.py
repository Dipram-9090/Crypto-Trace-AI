"""ERC-20, ERC-721, and ERC-1155 Token Transfer Tracker."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("cryptotrace.blockchain.ethereum.tokens")

ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


class TokenTracker:
    """Parses EVM event logs to detect stablecoin (USDT, USDC, DAI) and NFT transfers."""

    @staticmethod
    def parse_transfer_logs(receipt_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transfers = []
        for log in receipt_logs:
            topics = log.get("topics", [])
            if topics and topics[0] == ERC20_TRANSFER_TOPIC and len(topics) >= 3:
                # Addresses are padded 32 bytes in topics
                sender = "0x" + topics[1][-40:]
                receiver = "0x" + topics[2][-40:]
                raw_data = log.get("data", "0x0")
                try:
                    amount = int(raw_data, 16) if isinstance(raw_data, str) else 0
                except ValueError:
                    amount = 0

                transfers.append({
                    "contract": log.get("address", "0x00"),
                    "from": sender,
                    "to": receiver,
                    "raw_amount": amount,
                    "token_type": "ERC20"
                })
        return transfers
