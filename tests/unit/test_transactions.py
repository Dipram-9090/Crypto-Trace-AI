"""
Unit tests for Bitcoin transaction data structure.
"""

from src.cryptotrace.blockchain.bitcoin.transaction import BitcoinTransaction, TxInput, TxOutput


def test_bitcoin_transaction_structure():
    tx = BitcoinTransaction(
        txid="TX_TEST_001",
        inputs=[TxInput(prev_txid="TX_PREV", vout=0, amount=2.5)],
        outputs=[TxOutput(address="1BTC001", amount=1.5, vout=0), TxOutput(address="1BTC002", amount=0.98, vout=1)],
        fee=0.02,
    )
    assert tx.total_input_amount == 2.5
    assert round(tx.total_output_amount, 2) == 2.48
    assert tx.fan_out_ratio == 2.0
