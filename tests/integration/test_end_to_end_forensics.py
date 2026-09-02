"""
End-to-end integration tests for CryptoTrace AI Bitcoin Forensics Pipeline.
Tests Ingestion -> Normalization -> UTXO Tracking -> Multi-hop Graph -> Address Clustering ->
Forensic Heuristics -> Risk Scoring -> Universal Search -> Pathfinding -> Case Dossier -> Report Export.
"""

import os
import pandas as pd
from src.cryptotrace.api.app import BlockchainAPIService


def test_end_to_end_forensic_pipeline():
    sample_csv = "data/sample/transactions.csv"
    assert os.path.exists(sample_csv), "Synthetic dataset transactions.csv must exist"

    df = pd.read_csv(sample_csv)
    service = BlockchainAPIService()

    # 1. Ingest
    ingest_res = service.ingest_dataframe(df, dataset_id="synthetic_demo_01")
    assert ingest_res["success"] is True
    assert ingest_res["data"]["indexed_transactions"] >= 20
    assert ingest_res["data"]["indexed_addresses"] >= 30
    assert ingest_res["data"]["indexed_clusters"] >= 1

    # 2. Search for high fan-out transaction
    search_tx = service.search("tx_fanout_dispersion_0001_" + "c" * 42)
    assert search_tx["success"] is True
    assert search_tx["data"]["type"] == "TRANSACTION"
    assert search_tx["data"]["risk"]["risk_level"] in ["HIGH", "CRITICAL"]

    # 3. Search for rapid relay address
    search_addr = service.search("1RapidRelayStartAddr000000000000")
    assert search_addr["success"] is True
    assert search_addr["data"]["type"] == "ADDRESS"

    # 4. Query k-hop graph
    graph_res = service.get_address_graph("1ConsolidationMasterVault9999999999", k_hops=2)
    assert graph_res["success"] is True
    assert len(graph_res["data"]["nodes"]) >= 5

    # 5. Query cluster
    cluster_res = service.get_cluster("CLUSTER_0001")
    assert cluster_res["success"] is True
    assert cluster_res["data"]["size"] >= 1

    # 6. Timeline analysis
    timeline_res = service.get_address_timeline("1PeelChainOriginAddr111111111111")
    assert timeline_res["success"] is True
    assert len(timeline_res["data"]["timeline"]) >= 1

    # 7. Flow Pathfinding
    path_res = service.find_path("1RapidRelayStartAddr000000000000", "1RapidRelayHop02Addr33333333333333")
    assert path_res["success"] is True
    assert path_res["data"]["paths_found"] >= 1

    # 8. Create Case & Generate Report
    case_res = service.create_case("Operation Swift Trace", "Forensic analysis of synthetic cluster and dispersion")
    cid = case_res["data"]["case_id"]
    service.case_manager.add_evidence_address(cid, "1ConsolidationMasterVault9999999999")
    service.case_manager.add_evidence_transaction(cid, "tx_fanout_dispersion_0001_" + "c" * 42)
    service.case_manager.add_note(cid, "Agent Lead", "Confirmed high fan-out pattern matching dispersion behavior")

    report_res = service.get_case_report(cid)
    assert report_res["success"] is True
    assert "Operation Swift Trace" in report_res["data"]["markdown"]
    assert "HIGH_FAN_OUT" in report_res["data"]["markdown"]
