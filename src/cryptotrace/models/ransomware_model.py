"""
BitcoinHeist Ransomware Detection Model.
Trained on address graph topological features (length, weight, count, looped, neighbors, income).
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import xgboost as xgb
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
import joblib
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class RansomwareClassifier:
    """Supervised classifier detecting ransomware families and high-risk address graph signatures."""
    def __init__(self, n_estimators: int = 150, max_depth: int = 5, learning_rate: float = 0.05, random_state: int = 42, **kwargs):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": random_state,
            "eval_metric": kwargs.get("eval_metric", "aucpr")
        }
        self.model = xgb.XGBClassifier(**self.params)
        self.feature_names: List[str] = ["length", "weight", "count", "looped", "neighbors", "income"]
        self.is_trained: bool = False

    def train(self, df_heist: pd.DataFrame) -> Dict[str, Any]:
        """Train on BitcoinHeist address features."""
        X = df_heist[self.feature_names].fillna(0.0)
        y = df_heist["is_ransomware"].astype(int)

        self.model.fit(X, y)
        self.is_trained = True

        probs = self.model.predict_proba(X)[:, 1]
        preds = (probs >= 0.5).astype(int)

        metrics = {
            "precision": float(precision_score(y, preds, zero_division=0)),
            "recall": float(recall_score(y, preds, zero_division=0)),
            "f1": float(f1_score(y, preds, zero_division=0)),
            "pr_auc": float(average_precision_score(y, probs)),
            "roc_auc": float(roc_auc_score(y, probs))
        }
        logger.info(f"Ransomware Model Metrics: PR-AUC={metrics['pr_auc']:.4f}, F1={metrics['f1']:.4f}")
        return metrics

    def predict_ransomware_prob(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Ransomware model has not been trained.")
        X_mat = X[self.feature_names] if set(self.feature_names).issubset(X.columns) else X
        return self.model.predict_proba(X_mat)[:, 1]

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "feature_names": self.feature_names, "params": self.params}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "RansomwareClassifier":
        data = joblib.load(filepath)
        obj = cls(**data.get("params", {}))
        obj.model = data["model"]
        obj.feature_names = data.get("feature_names", ["length", "weight", "count", "looped", "neighbors", "income"])
        obj.is_trained = True
        return obj
