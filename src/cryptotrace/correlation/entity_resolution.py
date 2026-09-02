"""
Entity Resolution across Multi-Input Spending and Co-located Network Endpoints.
"""

from typing import Dict, List, Set
import networkx as nx


class EntityResolver:
    """Combines Multi-Input Heuristics (Common-Input-Ownership) and Co-located IP Clustered Identities."""

    def __init__(self):
        self.wallet_graph = nx.Graph()

    def add_multi_input_transaction(self, input_addresses: List[str]):
        """Connect all input addresses as belonging to the same entity cluster."""
        if len(input_addresses) > 1:
            for i in range(len(input_addresses) - 1):
                self.wallet_graph.add_edge(input_addresses[i], input_addresses[i + 1])
        elif len(input_addresses) == 1:
            self.wallet_graph.add_node(input_addresses[0])

    def get_cluster(self, address: str) -> Set[str]:
        """Return all addresses resolved to the same cluster as the target address."""
        if address in self.wallet_graph:
            return nx.node_connected_component(self.wallet_graph, address)
        return {address}

    def get_all_clusters(self) -> List[Set[str]]:
        """Return list of all resolved entity wallet clusters."""
        return list(nx.connected_components(self.wallet_graph))
