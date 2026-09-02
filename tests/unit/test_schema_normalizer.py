"""
Unit tests for heterogeneous schema normalization and dataset validation.
"""

import pandas as pd
from src.cryptotrace.blockchain.ingestion.normalizer import (
    TransactionNormalizer,
    detect_schema_mapping,
    normalize_record_to_transaction,
)


def test_detect_schema_mapping():
    cols = ["transaction_id", "from_address", "to_address", "value", "fees", "block_time"]
    mapping = detect_schema_mapping(cols)
    assert mapping["txid"] == "transaction_id"
    assert mapping["input_addresses"] == "from_address"
    assert mapping["output_addresses"] == "to_address"
    assert mapping["output_amounts"] == "value"
    assert mapping["fee"] == "fees"
    assert mapping["timestamp"] == "block_time"


def test_normalize_dataframe_variations():
    data = [
        {
            "tx_hash": "tx_abc_111",
            "sender": "1SenderAddr111111111111111111111",
            "receiver": "1ReceiverAddr22222222222222222222",
            "amount": 1.5,
            "tx_fee": 0.0001,
            "date": "2026-01-01T12:00:00",
        },
        {
            "tx_hash": "tx_abc_222",
            "sender": "1SenderAddr222222222222222222222",
            "receiver": "1ReceiverAddr33333333333333333333",
            "amount": 2.0,
            "tx_fee": 0.0002,
            "date": "2026-01-01T13:00:00",
        },
        {
            "tx_hash": "tx_abc_111",  # Duplicate
            "sender": "1SenderAddr111111111111111111111",
            "receiver": "1ReceiverAddr22222222222222222222",
            "amount": 1.5,
            "tx_fee": 0.0001,
            "date": "2026-01-01T12:00:00",
        },
    ]
    df = pd.DataFrame(data)
    normalizer = TransactionNormalizer(dataset_id="test_dataset_01")
    txs, report = normalizer.normalize_dataframe(df)

    assert len(txs) == 2
    assert report.total_records == 3
    assert report.valid_records == 2
    assert report.duplicate_records == 1
    assert txs[0].txid == "tx_abc_111"
    assert txs[0].total_output_amount == 1.5
    assert txs[0].fee == 0.0001
