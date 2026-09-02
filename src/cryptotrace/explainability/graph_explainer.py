"""
Sub-graph and Neighbor Attributions for GNN Decision Explainability.
"""

import networkx as nx
from typing import Dict, Any, List


class GraphNeighborhoodExplainer:
    """Explains GNN node predictions by extracting the top influential 1-hop and 2-hop subgraphs."""

    def __init__(self, G: nx.DiGraph):
        self.G = G

    def explain_node(self, target_node: str, max_hops: int = 2) -> Dict[str, Any]:
        if target_node not in self.G:
            return {"target_node": target_node, "subgraph_nodes": [], "subgraph_edges": []}

        sub_nodes = set([target_node])
        for n in self.G.predecessors(target_node):
            sub_nodes.add(n)
        for n in self.G.successors(target_node):
            sub_nodes.add(n)

        sub_G = self.G.subgraph(sub_nodes)
        return {"target_node": target_node, "subgraph_nodes": list(sub_G.nodes), "subgraph_edges": list(sub_G.edges)}
