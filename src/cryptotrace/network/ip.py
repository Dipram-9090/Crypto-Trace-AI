"""
IP Address and Subnet Validation & Analysis.
"""

import ipaddress
from typing import Optional, Dict, Any


def analyze_ip_address(ip_str: str) -> Dict[str, Any]:
    """Parse IP address and determine scope, type, and properties."""
    if not ip_str or not isinstance(ip_str, str):
        return {"ip": str(ip_str), "is_valid": False}

    clean_ip = ip_str.strip()
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
        return {
            "ip": clean_ip,
            "is_valid": True,
            "version": ip_obj.version,
            "is_private": ip_obj.is_private,
            "is_loopback": ip_obj.is_loopback,
            "is_multicast": ip_obj.is_multicast,
            "is_global": ip_obj.is_global,
        }
    except ValueError:
        return {"ip": clean_ip, "is_valid": False}
