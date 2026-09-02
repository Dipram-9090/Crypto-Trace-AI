"""
Address Encoding Format Classifier.
Identifies script types, witness versions, and network targets.
"""

from typing import Dict, Any


def classify_address_encoding(address: str) -> str:
    """Classify encoding type: P2PKH, P2SH, P2WPKH, P2WSH, P2TR, TESTNET, or SYNTHETIC."""
    if not address or not isinstance(address, str):
        return "UNKNOWN"
    addr = address.strip()

    if addr.startswith(("1BTC", "EPP_", "1BH_", "SYN_", "TEST_")):
        return "SYNTHETIC_BENCHMARK"
    elif addr.startswith("1"):
        return "P2PKH_LEGACY"
    elif addr.startswith("3"):
        return "P2SH_SCRIPT"
    elif addr.lower().startswith("bc1q"):
        return "P2WPKH_SEGWIT" if len(addr) <= 42 else "P2WSH_SEGWIT"
    elif addr.lower().startswith("bc1p"):
        return "P2TR_TAPROOT"
    elif addr.startswith(("m", "n", "2")) or addr.lower().startswith("tb1"):
        return "TESTNET"
    elif addr.lower().startswith("bcrt1"):
        return "REGTEST"
    return "NON_STANDARD"


def inspect_address_details(address: str) -> Dict[str, Any]:
    """Provide comprehensive metadata attributes of an address."""
    encoding = classify_address_encoding(address)
    network = "TESTNET" if encoding in ["TESTNET", "REGTEST"] else "MAINNET"
    is_segwit = encoding in ["P2WPKH_SEGWIT", "P2WSH_SEGWIT", "P2TR_TAPROOT"]
    is_taproot = encoding == "P2TR_TAPROOT"
    
    return {
        "address": address,
        "encoding_type": encoding,
        "network": network,
        "is_segwit": is_segwit,
        "is_taproot": is_taproot,
        "witness_version": 1 if is_taproot else (0 if is_segwit else None),
    }
