"""
Data schema definitions and type specifications.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CanonicalTransaction:
    txid: str
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    input_addresses: List[str]
    output_addresses: List[str]
    input_amounts: List[float]
    output_amounts: List[float]
    fee: float
    script_type: str
    src_country: str
    dst_country: str
    src_asn: str
    dst_asn: str
    label: int
    entity_type: str
