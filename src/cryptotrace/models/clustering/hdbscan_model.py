"""
Behavioral Entity Clustering & Dimensionality Reduction Engine.
Discovers distinct transaction/wallet behavioral archetypes using DBSCAN/HDBSCAN and PCA.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib


class BehavioralClusterer:
    """Unsupervised clustering engine identifying behavioral groups (e.g., mixing rings, exchange clusters)."""
    def __init__(self, eps: float = 1.5, min_samples: int = 5, n_components: int = 2):
        self.eps = eps
        self.min_samples = min_samples
        self.n_components = n_components
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components, random_state=42)
        self.clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        self.feature_names: List[str] = []
        self.is_fitted = False

    def fit_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Fits scaler, PCA, and clustering, returning cluster labels and 2D coordinates."""
        self.feature_names = list(X.columns)
        X_clean = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        X_scaled = self.scaler.fit_transform(X_clean)
        coords_2d = self.pca.fit_transform(X_scaled)
        labels = self.clusterer.fit_predict(X_scaled)
        self.is_fitted = True
        return labels, coords_2d

    def summarize_clusters(self, df: pd.DataFrame, cluster_labels: np.ndarray) -> pd.DataFrame:
        """Computes statistical summaries for each discovered behavioral cluster."""
        df_temp = df.copy()
        df_temp["cluster"] = cluster_labels

        summary = []
        for c in sorted(list(set(cluster_labels))):
            c_df = df_temp[df_temp["cluster"] == c]
            label_name = "Noise / Outliers" if c == -1 else f"Cluster {c}"
            summary.append({
                "Cluster ID": c,
                "Name": label_name,
                "Entity Count": len(c_df),
                "Avg Risk Score": round(float(c_df.get("composite_risk_score", pd.Series([0.0])).mean()), 1),
                "Avg Fan-Out": round(float(c_df.get("fan_out_ratio", pd.Series([1.0])).mean()), 2),
                "Avg Velocity (TXs/24h)": round(float(c_df.get("wallet_txs_last_24h", pd.Series([0.0])).mean()), 1),
                "Avg Shared IP Index": round(float(c_df.get("shared_infrastructure_indicator", pd.Series([0.0])).mean()), 2)
            })

        return pd.DataFrame(summary)

    def save(self, filepath: str):
        joblib.dump({
            "scaler": self.scaler,
            "pca": self.pca,
            "clusterer": self.clusterer,
            "feature_names": self.feature_names
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> "BehavioralClusterer":
        data = joblib.load(filepath)
        obj = cls()
        obj.scaler = data["scaler"]
        obj.pca = data["pca"]
        obj.clusterer = data["clusterer"]
        obj.feature_names = data["feature_names"]
        obj.is_fitted = True
        return obj
