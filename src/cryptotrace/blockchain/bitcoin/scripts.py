"""
Bitcoin Script classification and opcode analysis.
Supports P2PKH, P2SH, P2WPKH, P2WSH, P2TR, Multisig, OP_RETURN, P2PK, and non-standard scripts.
"""

from typing import Optional, Dict, Any, Tuple


def identify_script_type(script_hex: str) -> str:
    """Identify Bitcoin script type from scriptPubKey hex."""
    if not script_hex or not isinstance(script_hex, str):
        return "unknown"
    s = script_hex.strip().lower()

    if s.startswith("6a"):
        return "op_return"
    elif s.startswith("76a914") and s.endswith("88ac") and len(s) == 50:
        return "p2pkh"
    elif s.startswith("a914") and s.endswith("87") and len(s) == 46:
        return "p2sh"
    elif s.startswith("0014") and len(s) == 44:
        return "p2wpkh"
    elif s.startswith("0020") and len(s) == 68:
        return "p2wsh"
    elif s.startswith("5120") and len(s) == 68:
        return "p2tr"
    elif s.endswith("ae"):
        return "multisig"
    elif s.endswith("ac") and (len(s) == 70 or len(s) == 134):
        return "p2pk"
    
    # Fallbacks for prefixes
    if s.startswith("76a9"):
        return "p2pkh"
    elif s.startswith("a9"):
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


def parse_op_return_payload(script_hex: str) -> Optional[str]:
    """Safely decode OP_RETURN arbitrary metadata payload if present."""
    if not script_hex or not isinstance(script_hex, str):
        return None
    s = script_hex.strip().lower()
    if not s.startswith("6a"):
        return None
    try:
        raw_bytes = bytes.fromhex(s)
        if len(raw_bytes) < 2:
            return None
        # Skip OP_RETURN (0x6a) and pushdata length byte(s)
        push_len = raw_bytes[1]
        data_bytes = raw_bytes[2:2 + push_len]
        try:
            return data_bytes.decode("utf-8", errors="replace")
        except Exception:
            return data_bytes.hex()
    except Exception:
        return None


def disassemble_script_opcodes(script_hex: str) -> str:
    """Produce human-readable opcode disassembly of a script."""
    stype = identify_script_type(script_hex)
    if stype == "p2pkh":
        return "OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG"
    elif stype == "p2sh":
        return "OP_HASH160 <scriptHash> OP_EQUAL"
    elif stype == "p2wpkh":
        return "OP_0 <20-byte-key-hash>"
    elif stype == "p2wsh":
        return "OP_0 <32-byte-script-hash>"
    elif stype == "p2tr":
        return "OP_1 <32-byte-taproot-output-key>"
    elif stype == "op_return":
        payload = parse_op_return_payload(script_hex)
        return f"OP_RETURN {payload or '<data>'}"
    elif stype == "multisig":
        return "OP_M <pubkeys...> OP_N OP_CHECKMULTISIG"
    return "UNKNOWN_SCRIPT"
