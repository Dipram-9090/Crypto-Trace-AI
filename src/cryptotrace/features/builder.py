"""
End-to-end Multi-modal Feature Builder Pipeline.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
import networkx as nx
from src.cryptotrace.features.transaction import extract_transaction_features
from src.cryptotrace.features.wallet import WalletTracker
from src.cryptotrace.features.network import NetworkTracker
from src.cryptotrace.features.temporal import TemporalTracker
from src.cryptotrace.features.graph import GraphFeatureExtractor


class FeatureBuilder:
    """Orchestrates transaction, wallet, temporal, network, and graph feature computation."""
    def __init__(self, G: Optional[nx.DiGraph] = None):
        self.wallet_tracker = WalletTracker()
        self.network_tracker = NetworkTracker()
        self.temporal_tracker = TemporalTracker()
        self.graph_extractor = GraphFeatureExtractor(G) if G is not None else None

    def build_features(self, df_clean: pd.DataFrame, G: Optional[nx.DiGraph] = None) -> pd.DataFrame:
        if G is not None and self.graph_extractor is None:
            self.graph_extractor = GraphFeatureExtractor(G)

        rows = []
        for idx, row in df_clean.iterrows():
            r = row.to_dict()
            txid = str(r.get("txid", ""))
            inputs = r.get("input_addresses", [])
            p_wallet = inputs[0] if isinstance(inputs, list) and len(inputs) > 0 else ""

            t_feats = extract_transaction_features(r)
            w_feats = self.wallet_tracker.extract_and_update(r)
            n_feats = self.network_tracker.extract_and_update(r)
            temp_feats = self.temporal_tracker.extract_and_update(r)
            g_feats = self.graph_extractor.get_node_features(txid) if self.graph_extractor else {}

            rows.append({
                "txid": txid,
                "timestamp": r.get("timestamp"),
                "datetime": r.get("datetime"),
                "src_ip": r.get("src_ip"),
                "dst_ip": r.get("dst_ip"),
                "primary_wallet": p_wallet,
                "src_country": r.get("src_country"),
                "src_asn": r.get("src_asn"),
                "label": int(r.get("label", 2)),
                "entity_type": str(r.get("entity_type", "NORMAL_USER")),
                **t_feats,
                **w_feats,
                **n_feats,
                **temp_feats,
                **g_feats
            })

        return pd.DataFrame(rows)
