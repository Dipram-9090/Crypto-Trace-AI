"""
Unit tests for blockchain graph construction, k-hop queries, and flow pathfinding.
"""

from src.cryptotrace.blockchain.graph.engine import BlockchainGraphEngine
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput


def test_graph_builder_and_khop():
    tx1 = BitcoinTransaction(
        txid="tx_g1",
        inputs=[TxInput(prev_txid="", vout=0, address="1AddrA", amount=5.0)],
        outputs=[TxOutput(address="1AddrB", amount=3.0, vout=0), TxOutput(address="1AddrC", amount=2.0, vout=1)],
    )
    tx2 = BitcoinTransaction(
        txid="tx_g2",
        inputs=[TxInput(prev_txid="tx_g1", vout=0, address="1AddrB", amount=3.0)],
        outputs=[TxOutput(address="1AddrD", amount=2.99, vout=0)],
    )

    engine = BlockchainGraphEngine()
    engine.build_from_transactions([tx1, tx2])

    metrics = engine.compute_graph_metrics()
    assert metrics["address_count"] == 4
    assert metrics["transaction_count"] == 2

    # Test 2-hop neighborhood from 1AddrA
    k_hop = engine.get_k_hop_subgraph("1AddrA", k_hops=2)
    node_ids = [n["id"] for n in k_hop["nodes"]]
    assert "1AddrA" in node_ids
    assert "tx_g1" in node_ids
    assert "1AddrB" in node_ids

    # Test flow pathfinding from 1AddrA to 1AddrD
    paths = engine.find_flow_paths("1AddrA", "1AddrD")
    assert len(paths) > 0
    assert paths[0]["path"] == ["1AddrA", "1AddrB", "1AddrD"]
    assert paths[0]["hop_count"] == 2
