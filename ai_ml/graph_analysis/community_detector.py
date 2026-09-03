"""Graph Community and Syndicate Cluster Detection."""

import logging
from typing import Dict, Any, List
import networkx as nx
import networkx.algorithms.community as nx_comm

logger = logging.getLogger("cryptotrace.ai_ml.graph.community")


class GraphCommunityDetector:
    """Discovers sub-networks, mixer pools, and fraud cartels using Louvain & Greedy Modularity algorithms."""

    def __init__(self, graph: nx.Graph = None):
        self.graph = graph

    def detect_communities(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Partitions network into dense communities and scores modularity."""
        undirected = graph.to_undirected()
        if len(undirected.nodes) < 2:
            return {"communities": [], "modularity": 0.0}

        try:
            communities = nx_comm.louvain_communities(undirected, seed=42)
        except Exception:
            communities = list(nx_comm.greedy_modularity_communities(undirected))

        comm_list = [list(c) for c in communities]
        modularity = nx_comm.modularity(undirected, communities) if communities else 0.0

        # Map each address to its community ID
        node_to_comm = {}
        for idx, comm in enumerate(comm_list):
            for node in comm:
                node_to_comm[node] = idx

        return {
            "num_communities": len(comm_list),
            "modularity_score": round(float(modularity), 4),
            "node_community_map": node_to_comm,
            "largest_cluster_size": max(len(c) for c in comm_list) if comm_list else 0
        }
