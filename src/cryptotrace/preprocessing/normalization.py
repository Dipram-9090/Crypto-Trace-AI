"""
Feature scaling and normalization utilities.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler
import joblib


class FeatureScaler:
    """Outlier-resistant feature scaler."""
    def __init__(self, method: str = "robust"):
        self.method = method
        self.scaler = RobustScaler() if method == "robust" else StandardScaler()
        self.feature_names = []

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        self.feature_names = list(X.columns)
        X_clean = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return self.scaler.fit_transform(X_clean)

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        X_clean = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return self.scaler.transform(X_clean)

    def save(self, filepath: str):
        joblib.dump({"scaler": self.scaler, "feature_names": self.feature_names, "method": self.method}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "FeatureScaler":
        data = joblib.load(filepath)
        obj = cls(method=data["method"])
        obj.scaler = data["scaler"]
        obj.feature_names = data["feature_names"]
        return obj
