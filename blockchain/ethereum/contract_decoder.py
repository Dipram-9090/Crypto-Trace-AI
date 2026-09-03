"""Smart Contract Interaction and Method Signature Decoder."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("cryptotrace.blockchain.ethereum.decoder")

KNOWN_SIGNATURES = {
    "0xa9059cbb": "transfer(address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
    "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "0xd7711425": "deposit(bytes32)",  # Tornado Cash Deposit
    "0x21a0adb6": "withdraw(bytes,bytes32,bytes32,address,address,uint256,uint256)"  # Tornado Cash Withdraw
}


class ContractDecoder:
    """Decodes 4-byte EVM function selectors and warns about privacy mixer interactions."""

    @staticmethod
    def decode_input(input_data: str) -> Dict[str, Any]:
        if not input_data or input_data == "0x" or len(input_data) < 10:
            return {"type": "native_transfer", "method": "transfer", "is_mixer": False}

        selector = input_data[:10].lower()
        method_name = KNOWN_SIGNATURES.get(selector, f"unknown_{selector}")
        is_mixer = selector in ["0xd7711425", "0x21a0adb6"]

        return {
            "type": "contract_call",
            "selector": selector,
            "method": method_name,
            "is_mixer": is_mixer,
            "raw_payload_length": len(input_data)
        }
