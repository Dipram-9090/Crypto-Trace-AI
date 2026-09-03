"""Multi-Hop Transaction Tracing and Peeling Chain Discovery Engine."""

import logging
from typing import Dict, Any, List, Set
import networkx as nx
import pandas as pd

logger = logging.getLogger("cryptotrace.ai_ml.graph.multihop")


class MultiHopGraphTracer:
    """Performs forward and backward multi-hop traversal to follow dirty funds across blockchain layers."""

    def __init__(self, graph: nx.DiGraph = None):
        self.graph = graph if graph is not None else nx.DiGraph()

    def build_from_dataframe(self, df: pd.DataFrame):
        """Constructs graph from edge dataframe."""
        self.graph = nx.DiGraph()
        for _, row in df.iterrows():
            src = str(row["sender"])
            dst = str(row["receiver"])
            amt = float(row.get("amount", 1.0))
            tx_h = str(row.get("tx_hash", ""))
            self.graph.add_edge(src, dst, amount=amt, tx_hash=tx_h)

    def trace_forward(self, start_address: str, max_depth: int = 4, min_amount: float = 0.0) -> Dict[str, Any]:
        """Traces where funds flowed forward starting from a suspect address."""
        start_node = str(start_address).lower()
        if start_node not in self.graph:
            return {"nodes": [], "edges": [], "max_depth_reached": 0}

        visited_nodes: Set[str] = {start_node}
        edges_traversed: List[Dict[str, Any]] = []
        frontier = [(start_node, 0)]

        while frontier:
            curr_node, depth = frontier.pop(0)
            if depth >= max_depth:
                continue

            for neighbor in self.graph.successors(curr_node):
                edge_data = self.graph.get_edge_data(curr_node, neighbor, default={})
                amt = edge_data.get("amount", 0.0)

                if amt >= min_amount:
                    edges_traversed.append({
                        "source": curr_node,
                        "target": neighbor,
                        "amount": amt,
                        "tx_hash": edge_data.get("tx_hash", ""),
                        "hop": depth + 1
                    })
                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        frontier.append((neighbor, depth + 1))

        return {
            "root_address": start_node,
            "total_hops": max_depth,
            "unique_addresses_reached": len(visited_nodes),
            "nodes": list(visited_nodes),
            "edges": edges_traversed
        }

    def detect_peeling_chains(self, start_address: str, length_threshold: int = 3) -> List[List[str]]:
        """Identifies linear peeling chain patterns (1 large output + 1 small peel repeat)."""
        chains = []
        curr = str(start_address).lower()
        current_chain = [curr]

        while True:
            succs = list(self.graph.successors(curr))
            if len(succs) == 2:  # Classic Bitcoin peel pattern (1 change + 1 small payment)
                # Pick successor with higher outgoing edge count or higher volume
                next_hop = succs[0]
                current_chain.append(next_hop)
                curr = next_hop
                if len(current_chain) > 20:
                    break
            else:
                break

        if len(current_chain) >= length_threshold:
            chains.append(current_chain)
        return chains
