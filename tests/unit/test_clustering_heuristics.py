"""
Unit tests for address clustering, change detection, peel chains, mixing, and entropy.
"""

from src.cryptotrace.blockchain.clustering.common_input import CommonInputClusterer
from src.cryptotrace.blockchain.heuristics.change_detection import ChangeAddressDetector
from src.cryptotrace.blockchain.heuristics.engine import (
    ForensicHeuristicsEngine,
    calculate_shannon_entropy,
)
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput


def test_common_input_clustering():
    # tx with 2 co-spending inputs (Addr1 + Addr2)
    tx1 = BitcoinTransaction(
        txid="tx_c1",
        inputs=[
            TxInput(prev_txid="", vout=0, address="1ClusterAddrA", amount=1.0),
            TxInput(prev_txid="", vout=0, address="1ClusterAddrB", amount=2.0),
        ],
        outputs=[TxOutput(address="1RecipientAddrX", amount=2.99, vout=0)],
    )
    # tx with Addr2 + Addr3
    tx2 = BitcoinTransaction(
        txid="tx_c2",
        inputs=[
            TxInput(prev_txid="", vout=0, address="1ClusterAddrB", amount=1.0),
            TxInput(prev_txid="", vout=0, address="1ClusterAddrC", amount=3.0),
        ],
        outputs=[TxOutput(address="1RecipientAddrY", amount=3.99, vout=0)],
    )

    clusterer = CommonInputClusterer()
    clusters = clusterer.cluster_transactions([tx1, tx2])

    # All 3 addresses should be in the same cluster
    c_a = clusterer.get_cluster_for_address("1ClusterAddrA")
    c_b = clusterer.get_cluster_for_address("1ClusterAddrB")
    c_c = clusterer.get_cluster_for_address("1ClusterAddrC")

    assert c_a is not None
    assert c_a.cluster_id == c_b.cluster_id == c_c.cluster_id
    assert len(c_a.addresses) == 3


def test_change_detection():
    detector = ChangeAddressDetector()
    tx = BitcoinTransaction(
        txid="tx_chg",
        inputs=[TxInput(prev_txid="", vout=0, address="1Sender", amount=5.0, script_type="p2wpkh")],
        outputs=[
            TxOutput(address="1Merchant", amount=1.0, vout=0, script_type="p2pkh"),  # round payment
            TxOutput(address="1SenderNewChange", amount=3.999, vout=1, script_type="p2wpkh"),  # script match
        ],
    )
    evals = detector.evaluate_outputs(tx)
    assert len(evals) == 2
    # 2nd output should have higher change probability
    assert evals[1]["change_probability"] > evals[0]["change_probability"]


def test_mixing_and_fanout_heuristics():
    engine = ForensicHeuristicsEngine()
    
    # High Fan-out
    tx_fanout = BitcoinTransaction(
        txid="tx_fo",
        inputs=[TxInput(prev_txid="", vout=0, address="1Src", amount=15.0)],
        outputs=[TxOutput(address=f"1Dst{i}", amount=1.0, vout=i) for i in range(12)],
    )
    signals = engine.analyze_transaction(tx_fanout)
    types = [s.type for s in signals]
    assert "HIGH_FAN_OUT" in types

    # Mixing-like CoinJoin pattern (equal outputs)
    tx_mix = BitcoinTransaction(
        txid="tx_mx",
        inputs=[TxInput(prev_txid="", vout=0, address=f"1In{i}", amount=0.1) for i in range(4)],
        outputs=[TxOutput(address=f"1Out{i}", amount=0.1, vout=i) for i in range(4)],
    )
    signals_mix = engine.analyze_transaction(tx_mix)
    types_mix = [s.type for s in signals_mix]
    assert "MIXING_LIKE_STRUCTURE" in types_mix


def test_shannon_entropy():
    # Identical values -> max entropy (1.0)
    ent_equal = calculate_shannon_entropy([1.0, 1.0, 1.0, 1.0])
    assert ent_equal == 1.0

    # Highly skewed values -> low entropy
    ent_skewed = calculate_shannon_entropy([100.0, 0.001])
    assert ent_skewed < 0.1
