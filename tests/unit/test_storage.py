"""
Unit tests for Parquet storage and DuckDB Query Engine.
"""

import os
import tempfile
import pandas as pd
from src.cryptotrace.storage.parquet_io import write_parquet, read_parquet
from src.cryptotrace.storage.duckdb_engine import DuckDBQueryEngine


def test_parquet_io():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        temp_path = f.name

    try:
        write_parquet(df, temp_path)
        read_df = read_parquet(temp_path)
        assert len(read_df) == 3
        assert list(read_df["a"]) == [1, 2, 3]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_duckdb_engine():
    df = pd.DataFrame(
        {
            "primary_wallet": ["W1", "W1", "W2"],
            "txid": ["T1", "T2", "T3"],
            "transaction_value": [1.0, 2.0, 0.5],
            "fee": [0.01, 0.01, 0.005],
            "src_ip": ["1.1.1.1", "1.1.1.1", "2.2.2.2"],
            "src_country": ["US", "US", "DE"],
            "src_asn": ["AS1", "AS1", "AS2"],
            "composite_risk_score": [50.0, 70.0, 20.0],
        }
    )
    engine = DuckDBQueryEngine()
    engine.register_dataframe("transactions", df)

    res = engine.query("SELECT COUNT(*) as cnt FROM transactions")
    assert res.iloc[0]["cnt"] == 3

    w_summary = engine.get_wallet_summary("transactions")
    assert len(w_summary) == 2
    assert w_summary.iloc[0]["primary_wallet"] == "W1"
