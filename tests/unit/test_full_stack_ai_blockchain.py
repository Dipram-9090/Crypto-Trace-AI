"""Unit tests for the Full-Stack AI/ML, Blockchain, and Backend modules."""

import pytest
import pandas as pd
import numpy as np

from ai_ml.data_preprocessing import TransactionCleaner, UTXONormalizer
from ai_ml.feature_engineering import FullFeaturePipeline
from ai_ml.models import FraudXGBoostClassifier, ForensicEnsembleScorer
from ai_ml.anomaly_detection import IsolationForestDetector
from ai_ml.graph_analysis import MultiHopGraphTracer, HaircutTaintAnalyzer
from ai_ml.explainability import ForensicSHAPExplainer, ForensicReportGenerator
from blockchain.ethereum import ContractDecoder
from blockchain.bitcoin import CoinJoinDetector
from blockchain.address_analyzer import OFACSanctionChecker, WalletAnalyzer
from backend.authentication import AuthHandler
from backend.services import AIService, TransactionService, WalletService


def test_transaction_cleaner():
    cleaner = TransactionCleaner()
    df = pd.DataFrame([
        {"tx_hash": "0x123", "amount": 10.5, "sender": "0xA", "receiver": "0xB", "timestamp": "2026-01-01 12:00:00"},
        {"tx_hash": "0x123", "amount": 10.5, "sender": "0xA", "receiver": "0xB", "timestamp": "2026-01-01 12:00:00"},
    ])
    cleaned = cleaner.clean_records(df)
    assert len(cleaned) == 1
    assert cleaner.validate_schema(cleaned) is True


def test_feature_pipeline():
    pipeline = FullFeaturePipeline()
    df = pd.DataFrame([
        {"tx_hash": "0x1", "sender": "0xa", "receiver": "0xb", "amount": 2.5, "timestamp": "2026-01-01 10:00:00"},
        {"tx_hash": "0x2", "sender": "0xb", "receiver": "0xc", "amount": 2.4, "timestamp": "2026-01-01 10:05:00"},
    ])
    tx_enriched, node_feats = pipeline.fit_transform(df)
    assert len(tx_enriched) == 2
    assert "log_amount" in tx_enriched.columns


def test_ensemble_scorer():
    ensemble = ForensicEnsembleScorer()
    res = ensemble.compute_composite_risk(
        xgb_score=0.9,
        gnn_score=0.8,
        anomaly_score=0.7,
        heuristic_score=0.5
    )
    assert res["risk_tier"] in ["HIGH", "CRITICAL"]
    assert 0.0 <= res["composite_risk_score"] <= 1.0


def test_coinjoin_detector():
    tx_mock = {
        "vin": [{"address": "addr1", "value": 0.5}, {"address": "addr2", "value": 0.5}],
        "vout": [
            {"address": "out1", "value": 0.1},
            {"address": "out2", "value": 0.1},
            {"address": "out3", "value": 0.1},
            {"address": "out4", "value": 0.1}
        ]
    }
    res = CoinJoinDetector.is_coinjoin(tx_mock)
    assert res["is_coinjoin"] is True
    assert res["equal_output_count"] == 4


def test_ofac_sanctions():
    is_hit = OFACSanctionChecker.is_sanctioned("0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c")
    assert is_hit is True
    is_clean = OFACSanctionChecker.is_sanctioned("0x1111111111111111111111111111111111111111")
    assert is_clean is False


def test_auth_jwt():
    pwd = "securepassword123"
    hashed = AuthHandler.hash_password(pwd)
    assert AuthHandler.verify_password(pwd, hashed) is True
    assert AuthHandler.verify_password("wrongpassword", hashed) is False

    token = AuthHandler.create_access_token({"sub": "tester", "role": "admin"})
    decoded = AuthHandler.decode_token(token)
    assert decoded["sub"] == "tester"
    assert decoded["role"] == "admin"


def test_services():
    ai_srv = AIService()
    benchmarks = ai_srv.get_model_benchmarks()
    assert "models" in benchmarks
    assert len(benchmarks["models"]) >= 4

    tx_srv = TransactionService()
    res = tx_srv.analyze_transaction("0xabc123")
    assert "risk_verdict" in res
    assert "explainability" in res
