"""
Graph Node and Edge Schema Definitions.
"""
from enum import Enum


class NodeType(Enum):
    TRANSACTION = "Transaction"
    WALLET = "Wallet"
    IP = "IP"
    ASN = "ASN"
    COUNTRY = "Country"


class EdgeRelationship(Enum):
    INPUT_FROM = "INPUT_FROM"
    OUTPUT_TO = "OUTPUT_TO"
    OBSERVED_TRANSACTION = "OBSERVED_TRANSACTION"
    TRANSMITTED_TO = "TRANSMITTED_TO"
    BELONGS_TO = "BELONGS_TO"
    LOCATED_IN = "LOCATED_IN"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    TEMPORALLY_FOLLOWS = "TEMPORALLY_FOLLOWS"
