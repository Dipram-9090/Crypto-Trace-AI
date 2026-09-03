"""One-Class Support Vector Machine for Novelty & Outlier Detection."""

import logging
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("cryptotrace.ai_ml.anomaly.ocsvm")


class OneClassSVMDetector:
    """Detects high-dimensional wallet behavioral novelty."""

    def __init__(self, kernel: str = "rbf", nu: float = 0.05, gamma: str = "scale"):
        self.scaler = StandardScaler()
        self.model = OneClassSVM(kernel=kernel, nu=nu, gamma=gamma)

    def fit(self, X: pd.DataFrame):
        """Fits standard scaler and One-Class SVM decision boundary."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        logger.info(f"One-Class SVM fitted on {len(X)} samples.")

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """Returns normalized score in [0.0, 1.0], with 1.0 being far outside the learned boundary."""
        X_scaled = self.scaler.transform(X)
        distances = self.model.decision_function(X_scaled)  # Negative values are outliers
        normalized = 1.0 / (1.0 + np.exp(distances))
        return normalized
