"""
Unit tests for Risk Scoring Engine and Alert Generator.
"""
import pytest
import pandas as pd
from src.scoring.risk_engine import RiskEngine
from src.investigation.alert_generator import AlertGenerator


def test_risk_engine():
    engine = RiskEngine(w_ml=0.50, w_anomaly=0.20, w_graph=0.20, w_behavioral=0.10)
    
    # Critical case
    score, tier = engine.compute_composite_risk(
        ml_prob=0.95,
        anomaly_score=90.0,
        graph_score=85.0,
        behavioral_score=75.0
    )
    assert score >= 80.0
    assert tier == "CRITICAL"

    # Low risk case
    score_low, tier_low = engine.compute_composite_risk(
        ml_prob=0.02,
        anomaly_score=10.0,
        graph_score=5.0,
        behavioral_score=10.0
    )
    assert score_low < 30.0
    assert tier_low == "LOW"


def test_alert_generator():
    data = [
        {
            "txid": "TX_CRIT",
            "primary_wallet": "1BTC_SUSP",
            "composite_risk_score": 92.5,
            "risk_level": "CRITICAL",
            "ml_probability": 0.94,
            "anomaly_score": 88.0,
            "graph_score": 82.0,
            "src_ip": "185.220.101.5",
            "src_asn": "AS13335",
            "timestamp": "2026-01-01 12:00:00"
        },
        {
            "txid": "TX_LOW",
            "primary_wallet": "1BTC_NORM",
            "composite_risk_score": 12.0,
            "risk_level": "LOW",
            "ml_probability": 0.03,
            "anomaly_score": 8.0,
            "graph_score": 5.0,
            "src_ip": "51.15.89.2",
            "src_asn": "AS24940",
            "timestamp": "2026-01-01 12:05:00"
        }
    ]
    df = pd.DataFrame(data)
    gen = AlertGenerator(min_risk_threshold=30.0)
    alerts = gen.generate_alerts(df)

    assert len(alerts) == 1
    assert alerts[0].alert_id == "ALERT_0001"
    assert alerts[0].risk_level == "CRITICAL"
    assert alerts[0].entity_id == "1BTC_SUSP"
