"""
CryptoTrace AI - Blockchain Domain Module.
Covers Bitcoin transaction data structures, UTXO tracking, address encodings, node RPC adapters,
graph analytics, common-input clustering, change detection, forensic heuristics, and explainable risk scoring.
"""

from src.cryptotrace.blockchain.models import (
    BitcoinTransaction,
    TxInput,
    TxOutput,
    BitcoinBlock,
    UTXO,
    AddressProfile,
    AddressCluster,
    ForensicSignal,
    RiskEvaluation,
    TimelineEvent,
    InvestigationCase,
    IngestionJob,
)
from src.cryptotrace.blockchain.bitcoin.utxo import UTXOSet
from src.cryptotrace.blockchain.bitcoin.scripts import (
    identify_script_type,
    parse_op_return_payload,
    disassemble_script_opcodes,
)
from src.cryptotrace.blockchain.bitcoin.parser import parse_rpc_raw_transaction
from src.cryptotrace.blockchain.addresses.validator import is_valid_bitcoin_address
from src.cryptotrace.blockchain.addresses.normalizer import normalize_address
from src.cryptotrace.blockchain.addresses.classifier import (
    classify_address_encoding,
    inspect_address_details,
)
from src.cryptotrace.blockchain.rpc.bitcoin_core import BitcoinCoreRPC
from src.cryptotrace.blockchain.ingestion.normalizer import (
    TransactionNormalizer,
    DatasetValidationReport,
)
from src.cryptotrace.blockchain.graph.engine import BlockchainGraphEngine
from src.cryptotrace.blockchain.clustering.common_input import CommonInputClusterer
from src.cryptotrace.blockchain.heuristics.change_detection import ChangeAddressDetector
from src.cryptotrace.blockchain.heuristics.engine import ForensicHeuristicsEngine
from src.cryptotrace.blockchain.scoring.risk_engine import BlockchainRiskEngine
from src.cryptotrace.blockchain.analysis.engine import BlockchainAnalysisEngine

__all__ = [
    "BitcoinTransaction",
    "TxInput",
    "TxOutput",
    "BitcoinBlock",
    "UTXOSet",
    "UTXO",
    "AddressProfile",
    "AddressCluster",
    "ForensicSignal",
    "RiskEvaluation",
    "TimelineEvent",
    "InvestigationCase",
    "IngestionJob",
    "identify_script_type",
    "parse_op_return_payload",
    "disassemble_script_opcodes",
    "parse_rpc_raw_transaction",
    "is_valid_bitcoin_address",
    "normalize_address",
    "classify_address_encoding",
    "inspect_address_details",
    "BitcoinCoreRPC",
    "TransactionNormalizer",
    "DatasetValidationReport",
    "BlockchainGraphEngine",
    "CommonInputClusterer",
    "ChangeAddressDetector",
    "ForensicHeuristicsEngine",
    "BlockchainRiskEngine",
    "BlockchainAnalysisEngine",
]
