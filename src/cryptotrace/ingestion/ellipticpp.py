"""
Elliptic++ Extended Graph & Wallet Ingestion Loader.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class EllipticPlusPlusLoader:
    """Loads Elliptic++ dual transaction and wallet/actor graphs."""

    def __init__(self, data_dir: str = "data/raw/ellipticpp"):
        self.data_dir = data_dir
        self.txs_features_file = os.path.join(data_dir, "txs_features.csv")
        self.txs_classes_file = os.path.join(data_dir, "txs_classes.csv")
        self.wallets_features_file = os.path.join(data_dir, "wallets_features.csv")
        self.wallets_classes_file = os.path.join(data_dir, "wallets_classes.csv")
        self.addr_tx_file = os.path.join(data_dir, "AddrTx_edgelist.csv")
        self.tx_addr_file = os.path.join(data_dir, "TxAddr_edgelist.csv")
        self.addr_addr_file = os.path.join(data_dir, "AddrAddr_edgelist.csv")

    def exists(self) -> bool:
        return os.path.exists(self.txs_features_file) and os.path.exists(self.wallets_features_file)

    def load(self) -> Dict[str, pd.DataFrame]:
        """Loads transaction and wallet features alongside multi-relational edgelists."""
        if not self.exists():
            logger.warning(f"Elliptic++ dataset not found in {self.data_dir}. Generating structured sample.")
            return self._generate_sample_ellipticpp()

        txs_df = pd.read_csv(self.txs_features_file)
        wallets_df = pd.read_csv(self.wallets_features_file)
        addr_tx = pd.read_csv(self.addr_tx_file) if os.path.exists(self.addr_tx_file) else pd.DataFrame()
        tx_addr = pd.read_csv(self.tx_addr_file) if os.path.exists(self.tx_addr_file) else pd.DataFrame()
        addr_addr = pd.read_csv(self.addr_addr_file) if os.path.exists(self.addr_addr_file) else pd.DataFrame()

        return {
            "transactions": txs_df,
            "wallets": wallets_df,
            "addr_tx": addr_tx,
            "tx_addr": tx_addr,
            "addr_addr": addr_addr,
        }

    def _generate_sample_ellipticpp(self, n_tx: int = 300, n_wallets: int = 150) -> Dict[str, pd.DataFrame]:
        np.random.seed(42)
        tx_ids = [f"EPP_TX_{i:05d}" for i in range(n_tx)]
        wallet_ids = [f"EPP_WALLET_{i:04d}" for i in range(n_wallets)]

        tx_df = pd.DataFrame(
            {
                "txId": tx_ids,
                "time_step": np.random.randint(1, 50, size=n_tx),
                "label": np.random.choice([0, 1, 2], size=n_tx, p=[0.75, 0.10, 0.15]),
                **{f"feat_{i}": np.random.randn(n_tx) for i in range(1, 30)},
            }
        )

        wallet_df = pd.DataFrame(
            {
                "address": wallet_ids,
                "label": np.random.choice([0, 1, 2], size=n_wallets, p=[0.80, 0.08, 0.12]),
                "degree": np.random.randint(1, 25, size=n_wallets),
                "total_sent_btc": np.random.exponential(2.5, size=n_wallets),
                "total_recv_btc": np.random.exponential(2.8, size=n_wallets),
                **{f"wallet_feat_{i}": np.random.randn(n_wallets) for i in range(1, 15)},
            }
        )

        addr_tx = pd.DataFrame({"address": np.random.choice(wallet_ids, size=n_tx), "txId": tx_ids})

        tx_addr = pd.DataFrame({"txId": tx_ids, "address": np.random.choice(wallet_ids, size=n_tx)})

        addr_addr = pd.DataFrame(
            {
                "input_address": np.random.choice(wallet_ids, size=n_tx // 2),
                "output_address": np.random.choice(wallet_ids, size=n_tx // 2),
            }
        )

        return {
            "transactions": tx_df,
            "wallets": wallet_df,
            "addr_tx": addr_tx,
            "tx_addr": tx_addr,
            "addr_addr": addr_addr,
        }
