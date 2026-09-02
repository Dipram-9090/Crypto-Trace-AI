"""
Unified feature engineering pipeline for CryptoTrace AI.
Extracts transaction, wallet, network, temporal, and topological features in strict chronological order.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import logging
from src.features.transaction_features import extract_transaction_features
from src.features.wallet_features import WalletTracker
from src.features.network_features import NetworkTracker
from src.features.temporal_features import TemporalTracker
from src.features.graph_features import GraphFeatureExtractor
import networkx as nx

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """
    Coordinates multi-modal feature extraction across transaction, temporal, network, and graph dimensions.
    """
    def __init__(self, windows_hours: List[int] = [1, 6, 24, 168], burst_threshold_sec: int = 60):
        self.windows_hours = windows_hours
        self.burst_threshold_sec = burst_threshold_sec

    def fit_transform(self, df: pd.DataFrame, G: nx.DiGraph = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Process transactions chronologically and extract feature matrix.
        Returns:
            features_df: DataFrame containing all numerical features + metadata (txid, label, entity_type)
            feature_names: List of numerical feature column names
        """
        if df.empty:
            return pd.DataFrame(), []

        # Ensure sorted chronologically to prevent temporal leakage
        df_sorted = df.sort_values("datetime").reset_index(drop=True)

        wallet_tracker = WalletTracker()
        network_tracker = NetworkTracker()
        temporal_tracker = TemporalTracker(self.windows_hours, self.burst_threshold_sec)
        graph_extractor = GraphFeatureExtractor(G) if G is not None else None

        records = []
        for idx, row in df_sorted.iterrows():
            row_dict = row.to_dict()
            txid = row_dict.get("txid")
            primary_wallet = row_dict.get("input_addresses", [""])[0] if row_dict.get("input_addresses") else ""

            # 1. Transaction level features
            tx_feats = extract_transaction_features(row_dict)

            # 2. Wallet state features
            w_feats = wallet_tracker.extract_and_update(row_dict)

            # 3. Network state features
            net_feats = network_tracker.extract_and_update(row_dict)

            # 4. Temporal velocity features
            temp_feats = temporal_tracker.extract_and_update(row_dict)

            # 5. Graph topology features
            g_feats = graph_extractor.get_node_features(txid) if graph_extractor else {
                "graph_degree": 0.0,
                "graph_in_degree": 0.0,
                "graph_out_degree": 0.0,
                "graph_pagerank": 0.0,
                "graph_2hop_neighbors": 0.0,
                "graph_3hop_neighbors": 0.0
            }

            combined = {
                "txid": txid,
                "timestamp": row_dict.get("timestamp"),
                "datetime": row_dict.get("datetime"),
                "src_ip": row_dict.get("src_ip"),
                "dst_ip": row_dict.get("dst_ip"),
                "primary_wallet": primary_wallet,
                "src_country": row_dict.get("src_country"),
                "src_asn": row_dict.get("src_asn"),
                "label": int(row_dict.get("label", 2)),
                "entity_type": str(row_dict.get("entity_type", "NORMAL_USER")),
                **tx_feats,
                **w_feats,
                **net_feats,
                **temp_feats,
                **g_feats
            }
            records.append(combined)

        features_df = pd.DataFrame(records)
        
        # Identify numerical feature columns
        meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
        feature_names = [c for c in features_df.columns if c not in meta_cols]

        logger.info(f"Extracted {len(feature_names)} features for {len(features_df)} transactions.")
        return features_df, feature_names
