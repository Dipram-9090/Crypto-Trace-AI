"""Graph Structural Feature Extractor using NetworkX."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import networkx as nx

logger = logging.getLogger("cryptotrace.ai_ml.features.graph")


class GraphFeatureExtractor:
    """Extracts topological graph features including PageRank, in/out degrees, clustering, and centrality."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph_from_dataframe(self, df: pd.DataFrame, src_col: str = "sender", dst_col: str = "receiver", weight_col: str = "amount") -> nx.DiGraph:
        """Constructs a directed weighted transaction graph."""
        self.graph = nx.DiGraph()
        for _, row in df.iterrows():
            src = str(row[src_col])
            dst = str(row[dst_col])
            weight = float(row.get(weight_col, 1.0))
            if self.graph.has_edge(src, dst):
                self.graph[src][dst]["weight"] += weight
                self.graph[src][dst]["count"] += 1
            else:
                self.graph.add_edge(src, dst, weight=weight, count=1)
        return self.graph

    def compute_node_features(self) -> pd.DataFrame:
        """Computes comprehensive network metrics for each address node."""
        if len(self.graph.nodes) == 0:
            return pd.DataFrame()

        in_degree = dict(self.graph.in_degree())
        out_degree = dict(self.graph.out_degree())
        in_weight = dict(self.graph.in_degree(weight="weight"))
        out_weight = dict(self.graph.out_degree(weight="weight"))

        # Centrality algorithms
        try:
            pagerank = nx.pagerank(self.graph, weight="weight", max_iter=100)
        except Exception:
            pagerank = {n: 1.0 / len(self.graph.nodes) for n in self.graph.nodes}

        # Undirected projections for clustering
        undirected_g = self.graph.to_undirected()
        clustering_coeff = nx.clustering(undirected_g)

        records = []
        for node in self.graph.nodes:
            in_deg = in_degree.get(node, 0)
            out_deg = out_degree.get(node, 0)
            in_w = in_weight.get(node, 0.0)
            out_w = out_weight.get(node, 0.0)

            # Ratios
            total_deg = in_deg + out_deg
            fan_ratio = (out_deg / (in_deg + 1e-5)) if in_deg > 0 else float(out_deg)
            balance_flow = in_w - out_w

            records.append({
                "address": node,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "total_degree": total_deg,
                "in_volume": in_w,
                "out_volume": out_w,
                "net_volume_flow": balance_flow,
                "fan_ratio": fan_ratio,
                "pagerank": pagerank.get(node, 0.0),
                "clustering_coefficient": clustering_coeff.get(node, 0.0)
            })

        return pd.DataFrame(records)
