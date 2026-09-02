"""
Unit tests for explainable risk scoring and tier categorization.
"""

from src.cryptotrace.blockchain.scoring.risk_engine import BlockchainRiskEngine
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput


def test_risk_engine_explainable_scoring():
    engine = BlockchainRiskEngine()

    # Low risk normal transaction
    tx_normal = BitcoinTransaction(
        txid="tx_norm",
        inputs=[TxInput(prev_txid="", vout=0, address="1NormIn", amount=1.0)],
        outputs=[TxOutput(address="1NormOut1", amount=0.5, vout=0), TxOutput(address="1NormOut2", amount=0.499, vout=1)],
    )
    eval_norm = engine.evaluate_transaction(tx_normal)
    assert eval_norm.risk_level in ["LOW", "MEDIUM"]
    assert eval_norm.risk_score < 60.0

    # Suspicious high fan-out transaction
    tx_fanout = BitcoinTransaction(
        txid="tx_high_risk",
        inputs=[TxInput(prev_txid="", vout=0, address="1SuspiciousIn", amount=50.0)],
        outputs=[TxOutput(address=f"1Drop{i}", amount=2.0, vout=i) for i in range(25)],
    )
    eval_suspicious = engine.evaluate_transaction(tx_fanout)
    assert len(eval_suspicious.signals) > 0
    assert eval_suspicious.risk_score > eval_norm.risk_score
    assert any(s.type in ["HIGH_FAN_OUT", "LARGE_VALUE_TRANSFER"] for s in eval_suspicious.signals)
