"""
CryptoTrace AI - Strongly Typed Blockchain & Forensic Data Models.
Provides standard dataclasses and structures for Bitcoin transactions, UTXOs,
addresses, clusters, graph edges, risk scores, forensic signals, and case management.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import json


@dataclass
class TxInput:
    """Represents a single Bitcoin transaction input (vin)."""
    prev_txid: str
    vout: int
    script_sig: str = ""
    sequence: int = 0xFFFFFFFF
    address: Optional[str] = None
    amount: float = 0.0
    witness: List[str] = field(default_factory=list)
    script_type: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prev_txid": self.prev_txid,
            "vout": self.vout,
            "script_sig": self.script_sig,
            "sequence": self.sequence,
            "address": self.address,
            "amount": self.amount,
            "witness": self.witness,
            "script_type": self.script_type,
        }


@dataclass
class TxOutput:
    """Represents a single Bitcoin transaction output (vout)."""
    address: str
    amount: float
    vout: int
    script_pubkey: str = ""
    script_type: str = "p2pkh"
    is_op_return: bool = False
    op_return_data: Optional[str] = None
    is_change: bool = False
    change_probability: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "amount": self.amount,
            "vout": self.vout,
            "script_pubkey": self.script_pubkey,
            "script_type": self.script_type,
            "is_op_return": self.is_op_return,
            "op_return_data": self.op_return_data,
            "is_change": self.is_change,
            "change_probability": self.change_probability,
        }


@dataclass
class BitcoinTransaction:
    """Canonical Bitcoin transaction representation with complete protocol metadata."""
    txid: str
    version: int = 2
    locktime: int = 0
    inputs: List[TxInput] = field(default_factory=list)
    outputs: List[TxOutput] = field(default_factory=list)
    fee: float = 0.0
    fee_rate: float = 0.0  # satoshis per vByte
    timestamp: Optional[str] = None
    block_height: Optional[int] = None
    block_hash: Optional[str] = None
    size: int = 0
    vsize: int = 0
    weight: int = 0
    is_coinbase: bool = False
    dataset_id: Optional[str] = None

    @property
    def total_input_amount(self) -> float:
        return sum(i.amount for i in self.inputs)

    @property
    def total_output_amount(self) -> float:
        return sum(o.amount for o in self.outputs)

    @property
    def input_addresses(self) -> List[str]:
        return [i.address for i in self.inputs if i.address]

    @property
    def output_addresses(self) -> List[str]:
        return [o.address for o in self.outputs if o.address]

    @property
    def fan_out_ratio(self) -> float:
        in_len = len(self.inputs)
        out_len = len(self.outputs)
        return out_len / in_len if in_len > 0 else float(out_len)

    @property
    def fan_in_ratio(self) -> float:
        in_len = len(self.inputs)
        out_len = len(self.outputs)
        return in_len / out_len if out_len > 0 else float(in_len)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.txid,
            "version": self.version,
            "locktime": self.locktime,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "fee": self.fee,
            "fee_rate": self.fee_rate,
            "timestamp": self.timestamp,
            "block_height": self.block_height,
            "block_hash": self.block_hash,
            "size": self.size,
            "vsize": self.vsize,
            "weight": self.weight,
            "is_coinbase": self.is_coinbase,
            "dataset_id": self.dataset_id,
            "total_input_amount": self.total_input_amount,
            "total_output_amount": self.total_output_amount,
        }


@dataclass
class BitcoinBlock:
    """Bitcoin Block data structure with header metadata and contained transactions."""
    hash: str
    height: int
    version: int = 1
    merkle_root: str = ""
    timestamp: int = 0
    bits: int = 0
    nonce: int = 0
    previous_block_hash: Optional[str] = None
    transactions: List[BitcoinTransaction] = field(default_factory=list)

    @property
    def transaction_count(self) -> int:
        return len(self.transactions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash,
            "height": self.height,
            "version": self.version,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "bits": self.bits,
            "nonce": self.nonce,
            "previous_block_hash": self.previous_block_hash,
            "transaction_count": self.transaction_count,
            "transactions": [tx.to_dict() for tx in self.transactions],
        }


@dataclass
class UTXO:
    """Represents an Unspent Transaction Output with lifecycle tracking."""
    txid: str
    vout: int
    address: str
    amount: float
    script_type: str = "p2pkh"
    block_height: Optional[int] = None
    created_at: Optional[str] = None
    is_spent: bool = False
    spent_in_txid: Optional[str] = None
    spent_at: Optional[str] = None

    @property
    def outpoint(self) -> str:
        return f"{self.txid}:{self.vout}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outpoint": self.outpoint,
            "txid": self.txid,
            "vout": self.vout,
            "address": self.address,
            "amount": self.amount,
            "script_type": self.script_type,
            "block_height": self.block_height,
            "created_at": self.created_at,
            "is_spent": self.is_spent,
            "spent_in_txid": self.spent_in_txid,
            "spent_at": self.spent_at,
        }


@dataclass
class AddressProfile:
    """Aggregated forensic profile for a single Bitcoin address."""
    address: str
    encoding_type: str = "UNKNOWN"
    network: str = "MAINNET"
    balance: float = 0.0
    total_received: float = 0.0
    total_sent: float = 0.0
    transaction_count: int = 0
    incoming_tx_count: int = 0
    outgoing_tx_count: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    cluster_id: Optional[str] = None
    is_cluster_head: bool = False
    risk_score: float = 0.0
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "encoding_type": self.encoding_type,
            "network": self.network,
            "balance": round(self.balance, 8),
            "total_received": round(self.total_received, 8),
            "total_sent": round(self.total_sent, 8),
            "transaction_count": self.transaction_count,
            "incoming_tx_count": self.incoming_tx_count,
            "outgoing_tx_count": self.outgoing_tx_count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "cluster_id": self.cluster_id,
            "is_cluster_head": self.is_cluster_head,
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
        }


@dataclass
class AddressCluster:
    """Heuristic identity cluster formed by common-input ownership."""
    cluster_id: str
    addresses: Set[str] = field(default_factory=set)
    primary_label: Optional[str] = None
    entity_type: str = "HEURISTIC_CLUSTER"
    confidence: float = 0.85
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def size(self) -> int:
        return len(self.addresses)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "size": self.size,
            "addresses": list(self.addresses),
            "primary_label": self.primary_label,
            "entity_type": self.entity_type,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }


@dataclass
class ForensicSignal:
    """An explainable forensic indicator with severity and detailed narrative."""
    type: str
    severity: str  # "low", "medium", "high", "critical"
    score: float
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "score": round(self.score, 1),
            "explanation": self.explanation,
            "metadata": self.metadata,
        }


@dataclass
class RiskEvaluation:
    """Composite risk assessment combining rule-based heuristics and ML anomaly scores."""
    entity_id: str
    entity_type: str  # "transaction", "address", "cluster"
    risk_score: float  # 0.0 to 100.0
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    heuristic_score: float = 0.0
    ml_anomaly_score: float = 0.0
    graph_score: float = 0.0
    behavioral_score: float = 0.0
    signals: List[ForensicSignal] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
            "heuristic_score": round(self.heuristic_score, 1),
            "ml_anomaly_score": round(self.ml_anomaly_score, 1),
            "graph_score": round(self.graph_score, 1),
            "behavioral_score": round(self.behavioral_score, 1),
            "signals": [s.to_dict() for s in self.signals],
        }


@dataclass
class TimelineEvent:
    """A chronological forensic timeline event."""
    timestamp: str
    event_type: str  # "INCOMING_FUNDS", "OUTGOING_FUNDS", "PEEL_STEP", "MIXING_ATTEMPT", "DORMANT_ACTIVATION", "RAPID_RELAY"
    txid: str
    address: Optional[str] = None
    amount: float = 0.0
    description: str = ""
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "txid": self.txid,
            "address": self.address,
            "amount": round(self.amount, 8),
            "description": self.description,
            "risk_level": self.risk_level,
        }


@dataclass
class InvestigationCase:
    """Investigation case dossier for tracking forensic evidence and generating reports."""
    case_id: str
    title: str
    description: str = ""
    status: str = "OPEN"  # "OPEN", "IN_PROGRESS", "CLOSED", "ESCALATED"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    selected_addresses: List[str] = field(default_factory=list)
    selected_transactions: List[str] = field(default_factory=list)
    selected_clusters: List[str] = field(default_factory=list)
    notes: List[Dict[str, str]] = field(default_factory=list)
    risk_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "selected_addresses": self.selected_addresses,
            "selected_transactions": self.selected_transactions,
            "selected_clusters": self.selected_clusters,
            "notes": self.notes,
            "risk_summary": self.risk_summary,
        }


@dataclass
class IngestionJob:
    """Status tracker for asynchronous or multi-step dataset ingestion."""
    job_id: str
    dataset_id: str
    status: str = "PENDING"  # "PENDING", "PROCESSING", "COMPLETED", "FAILED"
    stage: str = "UPLOADING"
    progress_pct: int = 0
    total_records: int = 0
    processed_records: int = 0
    invalid_records: int = 0
    transactions_count: int = 0
    addresses_count: int = 0
    clusters_count: int = 0
    suspicious_count: int = 0
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "dataset_id": self.dataset_id,
            "status": self.status,
            "stage": self.stage,
            "progress_pct": self.progress_pct,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "invalid_records": self.invalid_records,
            "transactions_count": self.transactions_count,
            "addresses_count": self.addresses_count,
            "clusters_count": self.clusters_count,
            "suspicious_count": self.suspicious_count,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
        }
