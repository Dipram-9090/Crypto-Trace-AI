"""
Ingestion schema definitions and validation constants.
"""

from src.cryptotrace.preprocessing.schema import CanonicalTransaction

MANDATORY_FIELDS = ["txid", "timestamp"]
OPTIONAL_FIELDS = [
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "input_addresses",
    "output_addresses",
    "input_amounts",
    "output_amounts",
    "fee",
    "script_type",
    "src_country",
    "src_asn",
    "label",
    "entity_type",
]
