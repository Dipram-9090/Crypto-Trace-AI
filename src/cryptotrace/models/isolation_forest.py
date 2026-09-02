"""
Unsupervised Isolation Forest anomaly detection model.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest
import joblib


class CryptoIsolationForest:
    """Unsupervised behavioral anomaly detector outputting normalized 0-100 anomaly scores."""
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
        self.feature_names = list(X_train.columns)
        self.model.fit(X_train)
        self.is_trained = True

        scores = self.predict_anomaly_score(X_train)
        return {
            "mean_anomaly_score": float(np.mean(scores)),
            "max_anomaly_score": float(np.max(scores)),
            "min_anomaly_score": float(np.min(scores))
        }

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        X_mat = X[self.feature_names] if self.feature_names else X
        raw_scores = self.model.decision_function(X_mat)
        normalized = (0.25 - raw_scores) / 0.60 * 100.0
        return np.clip(normalized, 0.0, 100.0)

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "feature_names": self.feature_names, "params": self.params}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "CryptoIsolationForest":
        data = joblib.load(filepath)
        obj = cls(**data.get("params", {}))
        obj.model = data["model"]
        obj.feature_names = data.get("feature_names", [])
        obj.is_trained = True
        return obj
