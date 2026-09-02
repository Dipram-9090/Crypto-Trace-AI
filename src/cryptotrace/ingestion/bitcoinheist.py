"""
BitcoinHeist Ransomware Dataset Ingestion Loader & Preprocessor.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BitcoinHeistLoader:
    """Loads and formats the BitcoinHeist address-level ransomware graph dataset."""

    def __init__(self, data_dir: str = "data/raw/bitcoinheist"):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, "BitcoinHeistData.csv")

    def exists(self) -> bool:
        return os.path.exists(self.data_file)

    def load(self) -> pd.DataFrame:
        """Loads address graph features: length, weight, count, looped, neighbors, income."""
        if not self.exists():
            logger.warning(f"BitcoinHeist dataset not found in {self.data_dir}. Generating sample distribution.")
            return self._generate_sample_bitcoinheist()

        logger.info(f"Loading BitcoinHeist dataset from {self.data_file}...")
        df = pd.read_csv(self.data_file)
        # Create binary ransomware flag: 0 = white (licit), 1 = ransomware family (CryptoLocker, Locky, etc.)
        df["is_ransomware"] = (df["label"].str.lower() != "white").astype(int)
        return df

    def _generate_sample_bitcoinheist(self, n_samples: int = 500) -> pd.DataFrame:
        np.random.seed(42)
        families = ["white", "CryptoLocker", "Locky", "Cerber", "WannaCry", "CryptXXX"]
        labels = np.random.choice(families, size=n_samples, p=[0.85, 0.04, 0.04, 0.03, 0.02, 0.02])

        addresses = [f"1BH_ADDR_{i:06d}" for i in range(n_samples)]
        years = np.random.randint(2014, 2019, size=n_samples)
        days = np.random.randint(1, 365, size=n_samples)

        lengths = np.random.exponential(5.0, size=n_samples).astype(int) + 1
        weights = np.random.exponential(1.5, size=n_samples)
        counts = np.random.poisson(3, size=n_samples) + 1
        loopeds = np.random.binomial(5, 0.15, size=n_samples)
        neighbors = np.random.poisson(4, size=n_samples) + 1
        incomes = np.random.exponential(50000000.0, size=n_samples)

        # Inflate graph looping and neighbor density for ransomware
        for i, lbl in enumerate(labels):
            if lbl != "white":
                loopeds[i] += np.random.randint(2, 8)
                counts[i] += np.random.randint(5, 20)
                weights[i] *= np.random.uniform(2.0, 5.0)

        df = pd.DataFrame(
            {
                "address": addresses,
                "year": years,
                "day": days,
                "length": lengths,
                "weight": weights,
                "count": counts,
                "looped": loopeds,
                "neighbors": neighbors,
                "income": incomes,
                "label": labels,
                "is_ransomware": (labels != "white").astype(int),
            }
        )
        return df
