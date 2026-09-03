"""Comprehensive Feature Pipeline Orchestrator."""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from .graph_features import GraphFeatureExtractor
from .temporal_features import TemporalFeatureExtractor
from .wallet_profiler import WalletFeatureProfiler

logger = logging.getLogger("cryptotrace.ai_ml.features.pipeline")


class FullFeaturePipeline:
    """Combines graph features, temporal cyclical features, and wallet profiling into a unified vector."""

    def __init__(self):
        self.graph_extractor = GraphFeatureExtractor()
        self.feature_columns = []

    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Transforms raw transactions into enriched transaction features and wallet-level feature matrix.

        Returns:
            (enriched_tx_df, wallet_features_df)
        """
        logger.info("Executing Full Feature Pipeline...")

        # 1. Temporal feature expansion
        tx_enriched = TemporalFeatureExtractor.extract_temporal_features(df)

        # 2. Graph topology features
        self.graph_extractor.build_graph_from_dataframe(tx_enriched)
        graph_feats = self.graph_extractor.compute_node_features()

        # 3. Wallet profiling
        wallet_feats = WalletFeatureProfiler.profile_wallets(tx_enriched)

        # Merge graph and wallet node features
        if not graph_feats.empty and not wallet_feats.empty:
            merged_nodes = pd.merge(wallet_feats, graph_feats, on="address", how="left").fillna(0)
        else:
            merged_nodes = wallet_feats if not wallet_feats.empty else graph_feats

        # Enrich transaction edges with sender & receiver graph properties
        if not merged_nodes.empty:
            # Sender prefix
            sender_info = merged_nodes.add_prefix("src_").rename(columns={"src_address": "sender"})
            receiver_info = merged_nodes.add_prefix("dst_").rename(columns={"dst_address": "receiver"})

            tx_enriched = tx_enriched.merge(sender_info, on="sender", how="left")
            tx_enriched = tx_enriched.merge(receiver_info, on="receiver", how="left").fillna(0)

        # Numerical amount log-transforms
        if "amount" in tx_enriched.columns:
            tx_enriched["log_amount"] = np.log1p(tx_enriched["amount"].clip(lower=0))

        logger.info(f"Pipeline completed. Enriched {len(tx_enriched)} transactions and {len(merged_nodes)} unique nodes.")
        return tx_enriched, merged_nodes
