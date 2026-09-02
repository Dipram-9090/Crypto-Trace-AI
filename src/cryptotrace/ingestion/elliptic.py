"""
Elliptic Bitcoin Dataset Ingestion & Feature Parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class EllipticDatasetLoader:
    """Loads and formats the Elliptic Bitcoin transaction graph dataset."""

    def __init__(self, data_dir: str = "data/raw/elliptic"):
        self.data_dir = data_dir
        self.features_file = os.path.join(data_dir, "elliptic_txs_features.csv")
        self.classes_file = os.path.join(data_dir, "elliptic_txs_classes.csv")
        self.edgelist_file = os.path.join(data_dir, "elliptic_txs_edgelist.csv")

    def exists(self) -> bool:
        return os.path.exists(self.features_file) and os.path.exists(self.classes_file)

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Loads features and edges with standardized column names and label mapping."""
        if not self.exists():
            logger.warning(f"Elliptic dataset not found in {self.data_dir}. Generating synthetic fallback schema.")
            return self._generate_sample_elliptic()

        logger.info(f"Loading Elliptic dataset from {self.data_dir}...")
        df_classes = pd.read_csv(self.classes_file)
        # Class mapping: '1' -> 1 (illicit), '2' -> 0 (licit), 'unknown' -> 2
        class_map = {"1": 1, "2": 0, "unknown": 2, 1: 1, 2: 0, 3: 2}
        df_classes["label"] = df_classes["class"].map(class_map).fillna(2).astype(int)

        df_features = pd.read_csv(self.features_file, header=None)
        # Feature columns: col 0 = txId, col 1 = time_step, col 2..166 = local & aggregated features
        feature_cols = ["txId", "time_step"] + [f"feat_{i}" for i in range(1, len(df_features.columns) - 1)]
        df_features.columns = feature_cols

        df_merged = pd.merge(df_features, df_classes[["txId", "label"]], on="txId", how="left")

        df_edges = (
            pd.read_csv(self.edgelist_file)
            if os.path.exists(self.edgelist_file)
            else pd.DataFrame(columns=["txId1", "txId2"])
        )
        return df_merged, df_edges

    def _generate_sample_elliptic(self, n_samples: int = 500) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate structured Elliptic sample data when full download is absent."""
        np.random.seed(42)
        tx_ids = [f"EL_TX_{i:06d}" for i in range(n_samples)]
        time_steps = np.random.randint(1, 50, size=n_samples)
        labels = np.random.choice([0, 1, 2], size=n_samples, p=[0.70, 0.10, 0.20])

        feats = np.random.randn(n_samples, 165)
        # Give illicit transactions higher variance and distinct feature signatures
        illicit_mask = labels == 1
        feats[illicit_mask, :10] += np.random.uniform(1.5, 3.5, size=(illicit_mask.sum(), 10))

        feat_dict = {f"feat_{i}": feats[:, i - 1] for i in range(1, 166)}
        df_merged = pd.DataFrame({"txId": tx_ids, "time_step": time_steps, "label": labels, **feat_dict})

        edges = []
        for i in range(n_samples - 1):
            if np.random.rand() < 0.15:
                edges.append({"txId1": tx_ids[i], "txId2": tx_ids[np.random.randint(i + 1, n_samples)]})
        df_edges = pd.DataFrame(edges)

        return df_merged, df_edges
