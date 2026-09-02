"""
Graph analytics and neighborhood sub-graph querying.
"""

import networkx as nx
from typing import Dict, Any, List, Optional


class GraphAnalytics:
    """Provides ego-network extraction, path finding, and community discovery."""

    def __init__(self, G: nx.DiGraph):
        self.G = G

    def extract_subgraph(self, target_node: str, hops: int = 2, max_nodes: int = 80) -> nx.DiGraph:
        if target_node not in self.G:
            return nx.DiGraph()

        G_undirected = self.G.to_undirected()
        sub_nodes = {target_node}
        cur_layer = {target_node}

        for _ in range(hops):
            next_layer = set()
            for n in cur_layer:
                next_layer.update(G_undirected.neighbors(n))
            sub_nodes.update(next_layer)
            cur_layer = next_layer
            if len(sub_nodes) >= max_nodes:
                break

        selected = list(sub_nodes)[:max_nodes]
        return self.G.subgraph(selected).copy()

    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        try:
            return nx.shortest_path(self.G.to_undirected(), source, target)
        except Exception:
            return None
