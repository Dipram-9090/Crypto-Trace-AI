"""
Unit tests for Risk Engine and Composite Scoring.
"""
from src.cryptotrace.scoring.risk_engine import RiskEngine


def test_risk_engine():
    engine = RiskEngine(w_ml=0.50, w_anomaly=0.20, w_graph=0.20, w_behavioral=0.10)
    score, tier = engine.compute_composite_risk(
        ml_prob=0.95,
        anomaly_score=90.0,
        graph_score=85.0,
        behavioral_score=75.0
    )
    assert score >= 80.0
    assert tier == "CRITICAL"
