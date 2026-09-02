"""
Bitcoin Script classification and opcode analysis.
"""

from typing import Optional


def identify_script_type(script_hex: str) -> str:
    """Identify Bitcoin script type from scriptPubKey hex."""
    if not script_hex:
        return "unknown"
    s = script_hex.lower()
    if s.startswith("76a914") and s.endswith("88ac"):
        return "p2pkh"
    elif s.startswith("a914") and s.endswith("87"):
        return "p2sh"
    elif s.startswith("0014"):
        return "p2wpkh"
    elif s.startswith("0020"):
        return "p2wsh"
    elif s.startswith("5120"):
        return "p2tr"
    elif "ae" in s:
        return "multisig"
    return "nonstandard"
