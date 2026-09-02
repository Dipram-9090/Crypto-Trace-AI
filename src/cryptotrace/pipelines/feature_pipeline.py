"""
Feature Engineering and Heterogeneous Graph Construction Pipeline.
"""

import os
import pandas as pd
from typing import Tuple
import networkx as nx
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.features.builder import FeatureBuilder
from src.cryptotrace.storage.parquet_io import write_parquet


def run_feature_pipeline(
    df_clean: pd.DataFrame, out_parquet: str = "data/processed/features.parquet"
) -> Tuple[pd.DataFrame, nx.DiGraph]:
    """Constructs heterogeneous forensic graph and calculates anti-leakage feature sets."""
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df_clean)

    feat_builder = FeatureBuilder(G)
    feat_df = feat_builder.build_features(df_clean, G)

    if out_parquet:
        write_parquet(feat_df, out_parquet)

    return feat_df, G
