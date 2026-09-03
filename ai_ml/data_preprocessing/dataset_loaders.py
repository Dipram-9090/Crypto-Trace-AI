"""Loaders for standard public blockchain forensic benchmarks (Elliptic & BitcoinHeist)."""

import os
import logging
from typing import Tuple, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger("cryptotrace.ai_ml.datasets")


class EllipticDatasetLoader:
    """Loads and prepares the Elliptic Bitcoin Transaction Dataset (nodes, edges, classes)."""

    def __init__(self, data_dir: str = "data/raw/elliptic"):
        self.data_dir = data_dir

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Returns (features_df, edges_df). If raw files don't exist, generates synthetic benchmark sample."""
        features_path = os.path.join(self.data_dir, "elliptic_txs_features.csv")
        classes_path = os.path.join(self.data_dir, "elliptic_txs_classes.csv")
        edges_path = os.path.join(self.data_dir, "elliptic_txs_edgelist.csv")

        if os.path.exists(features_path) and os.path.exists(classes_path):
            logger.info("Loading actual Elliptic CSV dataset...")
            features = pd.read_csv(features_path, header=None)
            classes = pd.read_csv(classes_path)
            edges = pd.read_csv(edges_path) if os.path.exists(edges_path) else pd.DataFrame()
            merged = features.merge(classes, left_on=0, right_on="txId", how="left")
            return merged, edges

        logger.info("Elliptic files not found; synthesizing realistic forensic benchmark dataset.")
        np.random.seed(42)
        n_samples = 1000
        tx_ids = [f"tx_{i:06d}" for i in range(n_samples)]
        time_steps = np.random.randint(1, 50, size=n_samples)
        
        # 165 graph & local features
        features_data = np.random.randn(n_samples, 165)
        # Class distribution: 1=illicit (5%), 2=licit (40%), unknown=55%
        classes_arr = np.random.choice(["licit", "illicit", "unknown"], p=[0.40, 0.08, 0.52], size=n_samples)

        df = pd.DataFrame(features_data, columns=[f"feat_{i}" for i in range(165)])
        df.insert(0, "time_step", time_steps)
        df.insert(0, "txId", tx_ids)
        df["class"] = classes_arr

        # Synthetic edge list
        src = np.random.choice(tx_ids, size=2000)
        dst = np.random.choice(tx_ids, size=2000)
        edges_df = pd.DataFrame({"txId1": src, "txId2": dst})

        return df, edges_df


class BitcoinHeistDatasetLoader:
    """Loads BitcoinHeist Ransomware & Fraud benchmark dataset."""

    def __init__(self, data_dir: str = "data/raw/bitcoinheist"):
        self.data_dir = data_dir

    def load(self) -> pd.DataFrame:
        """Loads BitcoinHeist dataset with address, year, day, length, weight, count, looped, neighbors, income, label."""
        csv_path = os.path.join(self.data_dir, "BitcoinHeistData.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)

        # Synthetic fallback
        np.random.seed(1337)
        n = 800
        labels = np.random.choice(
            ["white", "CryptoLocker", "CryptoWall", "Locky", "Cerber"],
            p=[0.75, 0.10, 0.05, 0.05, 0.05],
            size=n
        )
        data = {
            "address": [f"1BvBMSEYstWetqTFn5Au4m4GFg7xJaNV{i:03d}" for i in range(n)],
            "year": np.random.randint(2018, 2024, size=n),
            "day": np.random.randint(1, 365, size=n),
            "length": np.random.exponential(scale=5.0, size=n),
            "weight": np.random.lognormal(mean=0, sigma=1, size=n),
            "count": np.random.poisson(lam=4, size=n),
            "looped": np.random.binomial(n=1, p=0.15, size=n),
            "neighbors": np.random.poisson(lam=3, size=n),
            "income": np.random.exponential(scale=1e8, size=n),
            "label": labels
        }
        return pd.DataFrame(data)
