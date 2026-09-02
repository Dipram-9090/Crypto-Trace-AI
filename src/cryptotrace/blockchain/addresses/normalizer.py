"""
Bitcoin Address String Normalization & Cleansing.
"""

def normalize_address(address: str) -> str:
    """Normalize address string formatting."""
    if not address or not isinstance(address, str):
        return ""
    addr = address.strip()
    if addr.lower().startswith("bitcoin:"):
        addr = addr[8:].split("?")[0]
    return addr
