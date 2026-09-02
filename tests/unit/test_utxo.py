"""
Unit tests for UTXO set management.
"""

from src.cryptotrace.blockchain.bitcoin.utxo import UTXOSet


def test_utxo_lifecycle():
    utxo_set = UTXOSet()
    utxo_set.add_utxo("TX_01", 0, "1BTC_ALICE", 5.0)
    assert utxo_set.get_address_balance("1BTC_ALICE") == 5.0

    spent = utxo_set.spend_utxo("TX_01", 0, "TX_02")
    assert spent is not None
    assert spent.is_spent is True
    assert utxo_set.get_address_balance("1BTC_ALICE") == 0.0
