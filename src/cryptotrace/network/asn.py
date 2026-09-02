"""
Autonomous System (ASN) and Routing Intelligence.
"""

from typing import Dict, Any


def parse_asn_string(asn_str: str) -> Dict[str, Any]:
    """Parse ASN identifier and numeric value."""
    if not asn_str:
        return {"asn": "AS0", "asn_number": 0}
    clean = str(asn_str).strip().upper()
    if clean.startswith("AS"):
        num_str = clean[2:]
    else:
        num_str = clean
    try:
        num = int(num_str)
        return {"asn": f"AS{num}", "asn_number": num}
    except ValueError:
        return {"asn": clean, "asn_number": 0}
