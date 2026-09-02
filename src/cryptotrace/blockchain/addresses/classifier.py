"""
Address Encoding Format Classifier.
"""

def classify_address_encoding(address: str) -> str:
    """Classify encoding type: P2PKH, P2SH, P2WPKH, P2WSH, P2TR, or TESTNET."""
    if not address or not isinstance(address, str):
        return "UNKNOWN"
    addr = address.strip()

    if addr.startswith("1"):
        return "P2PKH_LEGACY"
    elif addr.startswith("3"):
        return "P2SH_SCRIPT"
    elif addr.startswith("bc1q"):
        return "P2WPKH_SEGWIT" if len(addr) <= 42 else "P2WSH_SEGWIT"
    elif addr.startswith("bc1p"):
        return "P2TR_TAPROOT"
    elif addr.startswith("m") or addr.startswith("n") or addr.startswith("2") or addr.startswith("tb1"):
        return "TESTNET"
    return "NON_STANDARD"
