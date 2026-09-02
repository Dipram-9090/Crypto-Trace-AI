"""
Forensic Investigation, Universal Search, Timeline & Flow Path Analysis Engine.
Provides unified query resolution for txid, address, block hash, block height, and cluster ID,
chronological timeline sequencing, and graph-guided fund flow pathfinding.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from src.cryptotrace.blockchain.models import (
    BitcoinTransaction,
    AddressProfile,
    TimelineEvent,
    RiskEvaluation,
)
from src.cryptotrace.blockchain.graph.engine import BlockchainGraphEngine
from src.cryptotrace.blockchain.clustering.common_input import CommonInputClusterer
from src.cryptotrace.blockchain.bitcoin.utxo import UTXOSet
from src.cryptotrace.blockchain.scoring.risk_engine import BlockchainRiskEngine
from src.cryptotrace.blockchain.addresses.validator import is_valid_bitcoin_address
from src.cryptotrace.blockchain.addresses.classifier import classify_address_encoding
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BlockchainAnalysisEngine:
    """Integrated forensic analytics workspace for Bitcoin investigations."""

    def __init__(
        self,
        graph_engine: Optional[BlockchainGraphEngine] = None,
        clusterer: Optional[CommonInputClusterer] = None,
        utxo_set: Optional[UTXOSet] = None,
        risk_engine: Optional[BlockchainRiskEngine] = None,
    ):
        self.graph_engine = graph_engine or BlockchainGraphEngine()
        self.clusterer = clusterer or CommonInputClusterer()
        self.utxo_set = utxo_set or UTXOSet()
        self.risk_engine = risk_engine or BlockchainRiskEngine()
        self.transactions: Dict[str, BitcoinTransaction] = {}
        self.address_profiles: Dict[str, AddressProfile] = {}
        self.tx_risk_evaluations: Dict[str, RiskEvaluation] = {}
        self.address_risk_evaluations: Dict[str, RiskEvaluation] = {}

    def index_transactions(self, transactions: List[BitcoinTransaction]):
        """Load and index transactions across all forensic engines."""
        self.transactions = {tx.txid: tx for tx in transactions}

        # 1. Process UTXOs
        for tx in transactions:
            self.utxo_set.process_transaction(tx)

        # 2. Build Graph
        self.graph_engine.build_from_transactions(transactions)

        # 3. Cluster addresses
        self.clusterer.cluster_transactions(transactions)

        # 4. Build Address Profiles
        self._build_address_profiles(transactions)

        # 5. Run Risk Scoring
        self._score_all()

    def _build_address_profiles(self, transactions: List[BitcoinTransaction]):
        """Compile comprehensive address profile metrics."""
        self.address_profiles.clear()
        
        addr_txs: Dict[str, List[Tuple[str, BitcoinTransaction, float]]] = {}
        
        for tx in transactions:
            for vin in tx.inputs:
                if vin.address:
                    addr_txs.setdefault(vin.address, []).append(("OUT", tx, vin.amount))
            for vout in tx.outputs:
                if vout.address and not vout.is_op_return:
                    addr_txs.setdefault(vout.address, []).append(("IN", tx, vout.amount))

        for addr, records in addr_txs.items():
            in_records = [r for r in records if r[0] == "IN"]
            out_records = [r for r in records if r[0] == "OUT"]

            tot_received = sum(r[2] for r in in_records)
            tot_sent = sum(r[2] for r in out_records)
            balance = self.utxo_set.get_address_balance(addr)

            # Sort by timestamp
            timestamps = [r[1].timestamp for r in records if r[1].timestamp]
            first_seen = min(timestamps) if timestamps else None
            last_seen = max(timestamps) if timestamps else None

            cluster = self.clusterer.get_cluster_for_address(addr)
            cluster_id = cluster.cluster_id if cluster else None

            encoding = classify_address_encoding(addr)

            profile = AddressProfile(
                address=addr,
                encoding_type=encoding,
                balance=balance,
                total_received=tot_received,
                total_sent=tot_sent,
                transaction_count=len(set(r[1].txid for r in records)),
                incoming_tx_count=len(in_records),
                outgoing_tx_count=len(out_records),
                first_seen=first_seen,
                last_seen=last_seen,
                cluster_id=cluster_id,
            )
            self.address_profiles[addr] = profile

    def _score_all(self):
        """Evaluate risk for all transactions and addresses."""
        self.tx_risk_evaluations.clear()
        self.address_risk_evaluations.clear()

        # Score transactions
        for tx in self.transactions.values():
            eval_result = self.risk_engine.evaluate_transaction(
                tx=tx,
                all_transactions=self.transactions,
            )
            self.tx_risk_evaluations[tx.txid] = eval_result

        # Score addresses
        metrics = self.graph_engine.compute_graph_metrics()
        pageranks = metrics.get("pagerank", {})

        for addr, profile in self.address_profiles.items():
            # Find related tx evaluations
            related_tx_evals = []
            for tx in self.transactions.values():
                if addr in tx.input_addresses or addr in tx.output_addresses:
                    if tx.txid in self.tx_risk_evaluations:
                        related_tx_evals.append(self.tx_risk_evaluations[tx.txid])

            pr = pageranks.get(addr, 0.0)
            addr_eval = self.risk_engine.evaluate_address(
                address=addr,
                transaction_evaluations=related_tx_evals,
                fan_in=profile.incoming_tx_count,
                fan_out=profile.outgoing_tx_count,
                pagerank=pr,
            )
            self.address_risk_evaluations[addr] = addr_eval
            profile.risk_score = addr_eval.risk_score
            profile.risk_level = addr_eval.risk_level

    def search(self, query: str) -> Dict[str, Any]:
        """
        Universal search resolver: intelligently detects whether query is
        a txid, address, cluster_id, block height, or block hash.
        """
        q = query.strip()
        if not q:
            return {"type": "UNKNOWN", "matched": False, "result": None}

        # 1. Match Cluster ID
        if q.upper().startswith("CLUSTER_") and q.upper() in self.clusterer.clusters:
            c = self.clusterer.clusters[q.upper()]
            return {
                "type": "CLUSTER",
                "matched": True,
                "cluster_id": c.cluster_id,
                "data": c.to_dict(),
            }

        # 2. Match Transaction ID
        if q in self.transactions:
            tx = self.transactions[q]
            risk = self.tx_risk_evaluations.get(q)
            return {
                "type": "TRANSACTION",
                "matched": True,
                "txid": tx.txid,
                "data": tx.to_dict(),
                "risk": risk.to_dict() if risk else None,
            }

        # 3. Match Address
        if q in self.address_profiles:
            profile = self.address_profiles[q]
            risk = self.address_risk_evaluations.get(q)
            return {
                "type": "ADDRESS",
                "matched": True,
                "address": q,
                "data": profile.to_dict(),
                "risk": risk.to_dict() if risk else None,
            }

        # 4. Check if valid address format even if not directly in dataset
        if is_valid_bitcoin_address(q):
            return {
                "type": "ADDRESS",
                "matched": False,
                "address": q,
                "message": "Valid Bitcoin address format, but no transactions found in loaded dataset.",
                "encoding": classify_address_encoding(q),
            }

        # 5. Check if numeric block height
        if q.isdigit():
            height = int(q)
            matching_txs = [t.to_dict() for t in self.transactions.values() if t.block_height == height]
            return {
                "type": "BLOCK_HEIGHT",
                "matched": len(matching_txs) > 0,
                "block_height": height,
                "transactions_found": len(matching_txs),
                "transactions": matching_txs,
            }

        return {
            "type": "UNKNOWN",
            "matched": False,
            "query": q,
            "message": "Identifier not found in dataset.",
        }

    def generate_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Generate chronological forensic timeline for an address or transaction.
        """
        timeline: List[TimelineEvent] = []

        # If entity is address
        if entity_id in self.address_profiles:
            for tx in self.transactions.values():
                is_input = entity_id in tx.input_addresses
                is_output = entity_id in tx.output_addresses
                
                if not (is_input or is_output):
                    continue

                ts = tx.timestamp or "UNKNOWN_TIME"
                risk_level = self.tx_risk_evaluations.get(tx.txid, RiskEvaluation(tx.txid, "tx", 0.0, "LOW")).risk_level

                if is_input:
                    amt = sum(vin.amount for vin in tx.inputs if vin.address == entity_id)
                    timeline.append(
                        TimelineEvent(
                            timestamp=ts,
                            event_type="OUTGOING_FUNDS",
                            txid=tx.txid,
                            address=entity_id,
                            amount=amt,
                            description=f"Sent {amt:.4f} BTC in tx {tx.txid[:8]}... to {len(tx.outputs)} outputs.",
                            risk_level=risk_level,
                        )
                    )
                if is_output:
                    amt = sum(vout.amount for vout in tx.outputs if vout.address == entity_id)
                    timeline.append(
                        TimelineEvent(
                            timestamp=ts,
                            event_type="INCOMING_FUNDS",
                            txid=tx.txid,
                            address=entity_id,
                            amount=amt,
                            description=f"Received {amt:.4f} BTC in tx {tx.txid[:8]}...",
                            risk_level=risk_level,
                        )
                    )

        # If entity is transaction
        elif entity_id in self.transactions:
            tx = self.transactions[entity_id]
            ts = tx.timestamp or "UNKNOWN_TIME"
            risk = self.tx_risk_evaluations.get(tx.txid, RiskEvaluation(tx.txid, "tx", 0.0, "LOW"))
            
            timeline.append(
                TimelineEvent(
                    timestamp=ts,
                    event_type="TRANSACTION_EXECUTION",
                    txid=tx.txid,
                    amount=tx.total_output_amount,
                    description=f"Transaction executed moving {tx.total_output_amount:.4f} BTC ({len(tx.inputs)} inputs -> {len(tx.outputs)} outputs).",
                    risk_level=risk.risk_level,
                )
            )

        timeline.sort(key=lambda x: x.timestamp)
        return [e.to_dict() for e in timeline]

    def get_investigation_dossier(self, identifier: str) -> Dict[str, Any]:
        """
        Produce a comprehensive 360-degree forensic investigation dossier for an address or transaction.
        """
        search_res = self.search(identifier)
        if not search_res.get("matched"):
            return search_res

        entity_type = search_res["type"]
        timeline = self.generate_timeline(identifier)
        graph_data = self.graph_engine.get_k_hop_subgraph(identifier, k_hops=2)

        dossier = {
            "identifier": identifier,
            "entity_type": entity_type,
            "overview": search_res.get("data"),
            "risk_evaluation": search_res.get("risk"),
            "timeline": timeline,
            "graph": graph_data,
        }

        if entity_type == "ADDRESS":
            profile = self.address_profiles.get(identifier)
            cluster = self.clusterer.get_cluster_for_address(identifier)
            unspent_utxos = self.utxo_set.get_unspent_for_address(identifier)
            dossier["cluster"] = cluster.to_dict() if cluster else None
            dossier["unspent_utxos"] = [u.to_dict() for u in unspent_utxos]
            dossier["active_balance"] = profile.balance if profile else 0.0

        return dossier
