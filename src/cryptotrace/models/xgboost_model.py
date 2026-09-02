"""
Supervised XGBoost binary classification model.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import xgboost as xgb
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
)
import joblib
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def compute_metrics_at_k(y_true: np.ndarray, y_probs: np.ndarray, k_values: List[int] = [10, 50, 100, 500]) -> Dict[str, float]:
    metrics = {}
    total_positives = int(np.sum(y_true))
    if total_positives == 0 or len(y_true) == 0:
        return metrics

    ranked_indices = np.argsort(y_probs)[::-1]
    sorted_y_true = y_true[ranked_indices]

    for k in k_values:
        actual_k = min(k, len(sorted_y_true))
        top_k_labels = sorted_y_true[:actual_k]
        pos_in_k = int(np.sum(top_k_labels))

        prec_at_k = pos_in_k / actual_k if actual_k > 0 else 0.0
        rec_at_k = pos_in_k / total_positives if total_positives > 0 else 0.0

        metrics[f"precision@{k}"] = round(prec_at_k, 4)
        metrics[f"recall@{k}"] = round(rec_at_k, 4)

    return metrics


class CryptoXGBoostClassifier:
    """Supervised XGBoost model with temporal evaluation and serialization."""
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        scale_pos_weight: float = 10.0,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
        **kwargs
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "scale_pos_weight": scale_pos_weight,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "random_state": random_state,
            "eval_metric": kwargs.get("eval_metric", "aucpr")
        }
        self.model = xgb.XGBClassifier(**self.params)
        self.feature_names: List[str] = []
        self.is_trained: bool = False

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        self.feature_names = list(X_train.columns)
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        self.is_trained = True

        train_preds = self.model.predict(X_train)
        train_probs = self.model.predict_proba(X_train)[:, 1]

        report = {
            "train_precision": float(precision_score(y_train, train_preds, zero_division=0)),
            "train_recall": float(recall_score(y_train, train_preds, zero_division=0)),
            "train_f1": float(f1_score(y_train, train_preds, zero_division=0)),
            "train_pr_auc": float(average_precision_score(y_train, train_probs)),
            "train_roc_auc": float(roc_auc_score(y_train, train_probs))
        }
        return report

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        X_mat = X[self.feature_names] if self.feature_names else X
        return self.model.predict_proba(X_mat)[:, 1]

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        probs = self.predict_proba(X_test)
        preds = (probs >= 0.5).astype(int)
        y_arr = y_test.to_numpy()

        cm = confusion_matrix(y_arr, preds).tolist()
        pr_k = compute_metrics_at_k(y_arr, probs, [10, 50, 100, 500])

        metrics = {
            "precision": float(precision_score(y_arr, preds, zero_division=0)),
            "recall": float(recall_score(y_arr, preds, zero_division=0)),
            "f1": float(f1_score(y_arr, preds, zero_division=0)),
            "pr_auc": float(average_precision_score(y_arr, probs)),
            "roc_auc": float(roc_auc_score(y_arr, probs)),
            "confusion_matrix": cm,
            **pr_k
        }
        return metrics

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "feature_names": self.feature_names, "params": self.params}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "CryptoXGBoostClassifier":
        data = joblib.load(filepath)
        obj = cls(**data.get("params", {}))
        obj.model = data["model"]
        obj.feature_names = data.get("feature_names", [])
        obj.is_trained = True
        return obj
