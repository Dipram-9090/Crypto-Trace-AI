"""Behavioral Clustering & Entity Grouping Detector."""

import os
import joblib
import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans

logger = logging.getLogger("cryptotrace.ai_ml.anomaly.clustering")


class BehavioralClusteringDetector:
    """Discovers syndicates, mixer pools, and behavioral cohorts via unsupervised clustering."""

    def __init__(self, n_clusters: int = 5, eps: float = 0.5, min_samples: int = 4):
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.cluster_profiles = {}

    def fit_predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """Fits clusters and identifies noise clusters (outliers = -1 in DBSCAN)."""
        kmeans_labels = self.kmeans.fit_predict(X)
        dbscan_labels = self.dbscan.fit_predict(X)

        outlier_indices = np.where(dbscan_labels == -1)[0].tolist()

        return {
            "kmeans_clusters": kmeans_labels.tolist(),
            "dbscan_clusters": dbscan_labels.tolist(),
            "outlier_count": len(outlier_indices),
            "outlier_indices": outlier_indices
        }

    def save(self, path: str = "ml-models/clustering/behavioral_clusterer.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"kmeans": self.kmeans, "dbscan": self.dbscan}, path)
