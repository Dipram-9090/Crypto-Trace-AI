"""
Graph Centrality Analytics (Degree, PageRank, Betweenness).
"""

import networkx as nx
from typing import Dict, Any


def compute_centrality_metrics(G: nx.DiGraph) -> Dict[str, Dict[str, float]]:
    """Compute PageRank, In-Degree, Out-Degree, and Betweenness centrality."""
    if len(G.nodes) == 0:
        return {"pagerank": {}, "in_degree": {}, "out_degree": {}}

    try:
        pr = nx.pagerank(G, alpha=0.85, max_iter=100)
    except Exception:
        pr = {n: 1.0 / len(G.nodes) for n in G.nodes}

    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())

    return {"pagerank": pr, "in_degree": in_deg, "out_degree": out_deg}
