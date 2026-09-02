"""
CryptoTrace AI - Blockchain Domain Module.
Covers Bitcoin transaction data structures, UTXO tracking, address encodings, and node RPC adapters.
"""

from src.cryptotrace.blockchain.bitcoin.transaction import BitcoinTransaction, TxInput, TxOutput
from src.cryptotrace.blockchain.bitcoin.block import BitcoinBlock
from src.cryptotrace.blockchain.bitcoin.utxo import UTXOSet, UTXO
from src.cryptotrace.blockchain.bitcoin.scripts import identify_script_type
from src.cryptotrace.blockchain.bitcoin.parser import parse_rpc_raw_transaction
from src.cryptotrace.blockchain.addresses.validator import is_valid_bitcoin_address
from src.cryptotrace.blockchain.addresses.normalizer import normalize_address
from src.cryptotrace.blockchain.addresses.classifier import classify_address_encoding
from src.cryptotrace.blockchain.rpc.bitcoin_core import BitcoinCoreRPC

__all__ = [
    "BitcoinTransaction",
    "TxInput",
    "TxOutput",
    "BitcoinBlock",
    "UTXOSet",
    "UTXO",
    "identify_script_type",
    "parse_rpc_raw_transaction",
    "is_valid_bitcoin_address",
    "normalize_address",
    "classify_address_encoding",
    "BitcoinCoreRPC",
]
