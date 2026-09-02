"""
Primary Supervised XGBoost Classifier.
"""
from src.cryptotrace.models.xgboost_model import CryptoXGBoostClassifier, compute_metrics_at_k

__all__ = ["CryptoXGBoostClassifier", "compute_metrics_at_k"]
