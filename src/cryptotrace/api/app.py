"""
Standardized REST API Service for Blockchain Forensics.
Provides offline endpoints for transactions, address profiles, multi-hop graphs,
entity clustering, timeline analytics, pathfinding, case management, and ingestion.
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from src.cryptotrace.blockchain.analysis.engine import BlockchainAnalysisEngine
from src.cryptotrace.blockchain.ingestion.normalizer import TransactionNormalizer
from src.cryptotrace.investigation.case_manager import CaseManager
from src.cryptotrace.investigation.report_generator import ForensicReportGenerator


class BlockchainAPIService:
    """REST API Service Controller for Bitcoin Blockchain Forensics."""

    def __init__(self):
        self.analysis_engine = BlockchainAnalysisEngine()
        self.case_manager = CaseManager()
        self.report_generator = ForensicReportGenerator(self.analysis_engine)
        self.current_dataset_id = "default_dataset"

    def _make_response(
        self,
        data: Any = None,
        success: bool = True,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        start_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Format standardized JSON API response envelope."""
        duration_ms = round((time.time() - start_time) * 1000.0, 2) if start_time else 0.0
        return {
            "success": success,
            "data": data,
            "meta": {
                "dataset_id": self.current_dataset_id,
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": duration_ms,
            },
            "error": {
                "code": error_code,
                "message": error_message,
            } if not success else None,
        }

    def ingest_dataframe(self, df: pd.DataFrame, dataset_id: str = "custom_dataset") -> Dict[str, Any]:
        """Ingest and index a pandas DataFrame."""
        t0 = time.time()
        self.current_dataset_id = dataset_id
        normalizer = TransactionNormalizer(dataset_id=dataset_id)
        transactions, report = normalizer.normalize_dataframe(df)
        self.analysis_engine.index_transactions(transactions)

        return self._make_response(
            data={
                "validation_report": report.to_dict(),
                "indexed_transactions": len(transactions),
                "indexed_addresses": len(self.analysis_engine.address_profiles),
                "indexed_clusters": len(self.analysis_engine.clusterer.clusters),
            },
            start_time=t0,
        )

    def get_transaction(self, txid: str) -> Dict[str, Any]:
        t0 = time.time()
        tx = self.analysis_engine.transactions.get(txid)
        if not tx:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Transaction {txid} not found", start_time=t0)
        risk = self.analysis_engine.tx_risk_evaluations.get(txid)
        return self._make_response(
            data={
                "transaction": tx.to_dict(),
                "risk_evaluation": risk.to_dict() if risk else None,
            },
            start_time=t0,
        )

    def get_transaction_risk(self, txid: str) -> Dict[str, Any]:
        t0 = time.time()
        risk = self.analysis_engine.tx_risk_evaluations.get(txid)
        if not risk:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Risk evaluation for {txid} not found", start_time=t0)
        return self._make_response(data=risk.to_dict(), start_time=t0)

    def get_address(self, address: str) -> Dict[str, Any]:
        t0 = time.time()
        profile = self.analysis_engine.address_profiles.get(address)
        if not profile:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Address {address} not found", start_time=t0)
        risk = self.analysis_engine.address_risk_evaluations.get(address)
        cluster = self.analysis_engine.clusterer.get_cluster_for_address(address)
        return self._make_response(
            data={
                "profile": profile.to_dict(),
                "risk_evaluation": risk.to_dict() if risk else None,
                "cluster": cluster.to_dict() if cluster else None,
            },
            start_time=t0,
        )

    def get_address_timeline(self, address: str) -> Dict[str, Any]:
        t0 = time.time()
        events = self.analysis_engine.generate_timeline(address)
        return self._make_response(data={"address": address, "timeline": events}, start_time=t0)

    def get_address_graph(self, address: str, k_hops: int = 2) -> Dict[str, Any]:
        t0 = time.time()
        graph_data = self.analysis_engine.graph_engine.get_k_hop_subgraph(address, k_hops=k_hops)
        return self._make_response(data=graph_data, start_time=t0)

    def get_cluster(self, cluster_id: str) -> Dict[str, Any]:
        t0 = time.time()
        cluster = self.analysis_engine.clusterer.clusters.get(cluster_id)
        if not cluster:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Cluster {cluster_id} not found", start_time=t0)
        return self._make_response(data=cluster.to_dict(), start_time=t0)

    def search(self, query: str) -> Dict[str, Any]:
        t0 = time.time()
        res = self.analysis_engine.search(query)
        return self._make_response(data=res, start_time=t0)

    def find_path(self, source_address: str, target_address: str, max_paths: int = 5) -> Dict[str, Any]:
        t0 = time.time()
        paths = self.analysis_engine.graph_engine.find_flow_paths(source_address, target_address, max_paths=max_paths)
        return self._make_response(
            data={
                "source": source_address,
                "target": target_address,
                "paths_found": len(paths),
                "paths": paths,
            },
            start_time=t0,
        )

    def create_case(self, title: str, description: str = "") -> Dict[str, Any]:
        t0 = time.time()
        case = self.case_manager.create_case(title, description)
        return self._make_response(data=case.to_dict(), start_time=t0)

    def get_case(self, case_id: str) -> Dict[str, Any]:
        t0 = time.time()
        case = self.case_manager.get_case(case_id)
        if not case:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Case {case_id} not found", start_time=t0)
        return self._make_response(data=case.to_dict(), start_time=t0)

    def get_case_report(self, case_id: str) -> Dict[str, Any]:
        t0 = time.time()
        case = self.case_manager.get_case(case_id)
        if not case:
            return self._make_response(success=False, error_code="NOT_FOUND", error_message=f"Case {case_id} not found", start_time=t0)
        md_report = self.report_generator.generate_markdown_report(case)
        return self._make_response(
            data={
                "case_id": case_id,
                "markdown": md_report,
            },
            start_time=t0,
        )
