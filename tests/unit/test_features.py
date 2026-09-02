"""
Unit tests for Feature extraction components.
"""
from src.cryptotrace.features.transaction import extract_transaction_features
from src.cryptotrace.features.temporal import TemporalTracker


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
    assert feats["fan_out_ratio"] > 1.0


def test_temporal_features():
    tracker = TemporalTracker()
    rec = {
        "datetime": "2026-01-01 10:00:00",
        "input_addresses": ["W100"],
        "src_ip": "185.220.101.5"
    }
    t_feats = tracker.extract_and_update(rec)
    assert "burst_score" in t_feats
    assert "wallet_txs_last_1h" in t_feats
