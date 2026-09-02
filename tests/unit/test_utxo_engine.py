"""
Unit tests for UTXO ledger engine, spending lifecycle, and double-spend detection.
"""

from src.cryptotrace.blockchain.bitcoin.utxo import UTXOSet
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput


def test_utxo_lifecycle():
    utxo_set = UTXOSet()
    
    # 1. Add UTXO
    u1 = utxo_set.add_utxo("tx1", 0, "1AliceAddress1111111111111111111", 5.0)
    assert utxo_set.get_address_balance("1AliceAddress1111111111111111111") == 5.0
    assert not u1.is_spent

    # 2. Spend UTXO
    spent = utxo_set.spend_utxo("tx1", 0, "tx2", spent_at="2026-01-01T10:00:00")
    assert spent is not None
    assert spent.is_spent
    assert utxo_set.get_address_balance("1AliceAddress1111111111111111111") == 0.0

    # 3. Double-spend detection
    double_spent = utxo_set.spend_utxo("tx1", 0, "tx3", spent_at="2026-01-01T10:05:00")
    assert len(utxo_set.double_spends) == 1
    assert utxo_set.double_spends[0]["attempted_spent_in"] == "tx3"


def test_utxo_process_transaction():
    utxo_set = UTXOSet()
    
    # Funding tx
    tx1 = BitcoinTransaction(
        txid="tx_fund",
        inputs=[TxInput(prev_txid="", vout=0, address="", amount=10.0)],
        outputs=[TxOutput(address="1AliceAddr111111111111111111111", amount=10.0, vout=0)],
        fee=0.0,
    )
    utxo_set.process_transaction(tx1)
    assert utxo_set.get_address_balance("1AliceAddr111111111111111111111") == 10.0

    # Spending tx
    tx2 = BitcoinTransaction(
        txid="tx_spend",
        inputs=[TxInput(prev_txid="tx_fund", vout=0, address="1AliceAddr111111111111111111111", amount=10.0)],
        outputs=[
            TxOutput(address="1BobAddr2222222222222222222222", amount=4.0, vout=0),
            TxOutput(address="1AliceChangeAddr3333333333333333", amount=5.999, vout=1),
        ],
        fee=0.001,
    )
    tot_in, tot_out, fee = utxo_set.process_transaction(tx2)
    assert tot_in == 10.0
    assert round(tot_out, 6) == 9.999
    assert round(fee, 6) == 0.001
    assert utxo_set.get_address_balance("1AliceAddr111111111111111111111") == 0.0
    assert utxo_set.get_address_balance("1BobAddr2222222222222222222222") == 4.0
    assert utxo_set.get_address_balance("1AliceChangeAddr3333333333333333") == 5.999
