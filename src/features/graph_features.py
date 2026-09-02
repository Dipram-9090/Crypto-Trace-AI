"""
Graph topological feature extraction for CryptoTrace AI.
Extracts centrality, PageRank, degree, and neighborhood density features.
"""

import networkx as nx
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class GraphFeatureExtractor:
    """
    Computes structural graph properties from entity and transaction graph.
    """

    def __init__(self, G: nx.DiGraph):
        self.G = G
        self.pagerank = {}
        self.in_degree = {}
        self.out_degree = {}
        self.degree = {}
        self._compute_metrics()

    def _compute_metrics(self):
        if len(self.G.nodes) == 0:
            return
        try:
            self.pagerank = nx.pagerank(self.G, alpha=0.85, max_iter=100)
        except Exception:
            self.pagerank = {n: 1.0 / len(self.G.nodes) for n in self.G.nodes}

        self.in_degree = dict(self.G.in_degree())
        self.out_degree = dict(self.G.out_degree())
        self.degree = dict(self.G.degree())

    def get_node_features(self, node_id: str) -> Dict[str, float]:
        if node_id not in self.G:
            return {
                "graph_degree": 0.0,
                "graph_in_degree": 0.0,
                "graph_out_degree": 0.0,
                "graph_pagerank": 0.0,
                "graph_2hop_neighbors": 0.0,
                "graph_3hop_neighbors": 0.0,
            }

        deg = float(self.degree.get(node_id, 0))
        in_deg = float(self.in_degree.get(node_id, 0))
        out_deg = float(self.out_degree.get(node_id, 0))
        pr = float(self.pagerank.get(node_id, 0.0))

        # 2-hop and 3-hop neighborhood approximation
        neighbors_1 = set(self.G.neighbors(node_id))
        neighbors_2 = set()
        for n1 in neighbors_1:
            neighbors_2.update(self.G.neighbors(n1))
        neighbors_2.discard(node_id)

        neighbors_3 = set()
        for n2 in list(neighbors_2)[:50]:  # Limit for performance
            neighbors_3.update(self.G.neighbors(n2))
        neighbors_3.discard(node_id)

        return {
            "graph_degree": deg,
            "graph_in_degree": in_deg,
            "graph_out_degree": out_deg,
            "graph_pagerank": pr * 1000.0,  # Scaled for numerical stability
            "graph_2hop_neighbors": float(len(neighbors_2)),
            "graph_3hop_neighbors": float(len(neighbors_3)),
        }
