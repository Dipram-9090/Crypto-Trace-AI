"""
Graph Community Detection and Component Analysis.
"""
import networkx as nx
from typing import List, Set


def detect_connected_components(G: nx.DiGraph) -> List[Set[str]]:
    """Detect weakly connected components across transaction-entity subgraphs."""
    if len(G.nodes) == 0:
        return []
    return list(nx.weakly_connected_components(G))
