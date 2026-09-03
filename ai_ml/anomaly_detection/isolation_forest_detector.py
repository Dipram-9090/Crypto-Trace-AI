"""Isolation Forest Anomaly Detector."""

import os
import joblib
import logging
from typing import Optional, List
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("cryptotrace.ai_ml.anomaly.iforest")


class IsolationForestDetector:
    """Detects unusual high-volume bursts and outlier transaction structures."""

    def __init__(self, contamination: float = 0.05, model_path: Optional[str] = "ml-models/isolation_forest/isolation_forest.pkl"):
        self.contamination = contamination
        self.model_path = model_path
        self.model = None
        self._load_or_init()

    def _load_or_init(self):
        if self.model_path and os.path.exists(self.model_path):
            try:
                loaded = joblib.load(self.model_path)
                self.model = loaded["model"] if isinstance(loaded, dict) and "model" in loaded else loaded
                logger.info(f"Loaded Isolation Forest from {self.model_path}")
                return
            except Exception as e:
                logger.warning(f"Could not load Isolation Forest from {self.model_path}: {e}")

        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame):
        """Fits the Isolation Forest on standard transaction matrices."""
        self.model.fit(X)
        logger.info(f"Isolation Forest trained on {len(X)} records.")

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        """Returns normalized anomaly score in [0.0, 1.0], where 1.0 represents the highest anomaly severity."""
        raw_scores = self.model.score_samples(X)  # Negative scores (lower = more anomalous)
        # Invert and normalize to [0, 1]
        normalized = -raw_scores
        min_v, max_v = normalized.min(), normalized.max()
        if max_v > min_v:
            scores = (normalized - min_v) / (max_v - min_v)
        else:
            scores = np.zeros(len(X))
        return scores

    def save(self, path: str = "ml-models/isolation_forest/isolation_forest.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"model": self.model}, path)
