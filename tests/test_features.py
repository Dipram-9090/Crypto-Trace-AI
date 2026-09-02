"""
Unit tests for Feature Pipeline and Tracker components.
"""
import pytest
import pandas as pd
from datetime import datetime
from src.features.transaction_features import extract_transaction_features
from src.features.feature_pipeline import FeaturePipeline
from src.graph.graph_builder import ForensicGraphBuilder


def test_transaction_features():
    rec = {
        "input_addresses": ["W1", "W2"],
        "output_addresses": ["W3", "W4", "W5"],
        "input_amounts": [1.0, 2.0],
        "output_amounts": [0.5, 0.5, 1.95],
        "fee": 0.05
    }
    feats = extract_transaction_features(rec)
    assert feats["input_count"] == 2.0
    assert feats["output_count"] == 3.0
    assert feats["total_input_amount"] == 3.0
    assert feats["total_output_amount"] == 2.95
    assert feats["fan_out_ratio"] > 1.0


def test_feature_pipeline():
    rows = [
        {
            "txid": "TX_01",
            "timestamp": "2026-01-01 10:00:00",
            "datetime": datetime(2026, 1, 1, 10, 0, 0),
            "src_ip": "185.220.101.5",
            "dst_ip": "51.15.89.2",
            "src_port": 54321,
            "dst_port": 8333,
            "input_addresses": ["W100"],
            "output_addresses": ["W200"],
            "input_amounts": [1.0],
            "output_amounts": [0.99],
            "fee": 0.01,
            "script_type": "p2pkh",
            "src_country": "Netherlands",
            "dst_country": "Germany",
            "src_asn": "AS13335",
            "dst_asn": "AS24940",
            "label": 0,
            "entity_type": "NORMAL_USER"
        }
    ]
    df = pd.DataFrame(rows)
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df)

    pipeline = FeaturePipeline()
    feat_df, names = pipeline.fit_transform(df, G)
    assert len(feat_df) == 1
    assert "wallet_tx_velocity_per_hour" in names
    assert "burst_score" in names
    assert "fan_out_ratio" in names
