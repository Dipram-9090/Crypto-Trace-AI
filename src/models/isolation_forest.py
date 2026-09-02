"""
Unsupervised Isolation Forest anomaly detection model for CryptoTrace AI.
Identifies statistical transaction anomalies and outputs normalized 0-100 anomaly scores.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
import joblib
import logging

logger = logging.getLogger(__name__)


class CryptoIsolationForest:
    """
    Unsupervised behavioral anomaly detector.
    """
    def __init__(self, n_estimators: int = 150, contamination: float = 0.08, random_state: int = 42, **kwargs):
        self.params = {
            "n_estimators": n_estimators,
            "contamination": contamination,
            "random_state": random_state
        }
        self.model = IsolationForest(**self.params)
        self.feature_names: List[str] = []
        self.is_trained: bool = False

    def train(self, X_train: pd.DataFrame) -> Dict[str, Any]:
        """Fit Isolation Forest on behavioral feature matrix."""
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train)
        self.is_trained = True

        scores = self.predict_anomaly_score(X_train)
        report = {
            "mean_anomaly_score": float(np.mean(scores)),
            "max_anomaly_score": float(np.max(scores)),
            "min_anomaly_score": float(np.min(scores)),
            "high_anomaly_count": int(np.sum(scores >= 70.0))
        }
        logger.info(f"Isolation Forest training complete. Summary: {report}")
        return report

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Compute anomaly score normalized to 0.0 - 100.0 range.
        Higher score = more anomalous.
        """
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        X_mat = X[self.feature_names] if self.feature_names else X
        # Decision function: negative values are anomalies, positive are normal
        raw_scores = self.model.decision_function(X_mat)
        # Invert and scale to 0-100
        # raw_scores typically range from ~ -0.35 (severe anomaly) to +0.25 (very normal)
        normalized = (0.25 - raw_scores) / 0.60 * 100.0
        clipped = np.clip(normalized, 0.0, 100.0)
        return clipped

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "feature_names": self.feature_names, "params": self.params}, filepath)
        logger.info(f"Saved Isolation Forest model to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "CryptoIsolationForest":
        data = joblib.load(filepath)
        obj = cls(**data.get("params", {}))
        obj.model = data["model"]
        obj.feature_names = data["feature_names"]
        obj.is_trained = True
        return obj
