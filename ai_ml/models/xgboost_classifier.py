"""XGBoost Fraud & Ransomware Risk Classification Model."""

import os
import joblib
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger("cryptotrace.ai_ml.models.xgboost")


class FraudXGBoostClassifier:
    """Supervised gradient boosting classifier for illicit transaction and ransomware identification."""

    def __init__(self, model_path: Optional[str] = "ml-models/xgboost/xgboost_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = []
        self._load_or_init()

    def _load_or_init(self):
        """Loads trained weights or initializes an XGBoost / GradientBoosting instance."""
        if self.model_path and os.path.exists(self.model_path):
            try:
                loaded = joblib.load(self.model_path)
                if isinstance(loaded, dict) and "model" in loaded:
                    self.model = loaded["model"]
                    self.feature_names = loaded.get("features", [])
                else:
                    self.model = loaded
                logger.info(f"Loaded XGBoost model from {self.model_path}")
                return
            except Exception as e:
                logger.warning(f"Could not load {self.model_path}: {e}")

        # Fallback initialization using scikit-learn or xgboost
        try:
            import xgboost as xgb
            self.model = xgb.XGBClassifier(
                n_estimators=150,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="logloss",
                random_state=42
            )
        except ImportError:
            from sklearn.ensemble import GradientBoostingClassifier
            self.model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)

    def fit(self, X: pd.DataFrame, y: np.ndarray, feature_names: Optional[List[str]] = None):
        """Trains the gradient boosted decision tree classifier."""
        self.feature_names = feature_names or (X.columns.tolist() if isinstance(X, pd.DataFrame) else [])
        self.model.fit(X, y)
        logger.info(f"Fitted model on {len(X)} samples with {len(self.feature_names)} features.")

    def predict_risk_score(self, X: pd.DataFrame) -> np.ndarray:
        """Outputs calibrated illicit risk probability in range [0.0, 1.0]."""
        if self.model is None:
            return np.zeros(len(X))
        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)
                return probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]
            else:
                preds = self.model.predict(X)
                return (preds == 1).astype(float)
        except Exception as e:
            logger.warning(f"Inference error in XGBoost: {e}. Falling back to baseline scoring.")
            return np.full(len(X), 0.25)

    def save(self, output_path: str = "ml-models/xgboost/xgboost_model.pkl"):
        """Saves model weights and feature column schema."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        joblib.dump({"model": self.model, "features": self.feature_names}, output_path)
        logger.info(f"Saved model to {output_path}")
