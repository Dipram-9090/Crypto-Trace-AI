"""Taint Analysis and Dirty Fund Attribution (Haircut & Poison Models)."""

import logging
from typing import Dict, Any, List, Set
import networkx as nx

logger = logging.getLogger("cryptotrace.ai_ml.graph.taint")


class HaircutTaintAnalyzer:
    """Calculates proportional taint propagation across multi-hop transactions (Haircut model)."""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def compute_taint_flow(self, illicit_origin: str, initial_taint_amount: float = 100.0, decay: float = 0.9, max_depth: int = 5) -> Dict[str, float]:
        """Propagates taint fraction downstream to all recipient addresses."""
        taint_scores: Dict[str, float] = {illicit_origin: 1.0}
        frontier = [(illicit_origin, 1.0, 0)]

        while frontier:
            node, current_taint, depth = frontier.pop(0)
            if depth >= max_depth:
                continue

            successors = list(self.graph.successors(node))
            if not successors:
                continue

            total_out = sum(self.graph[node][succ].get("amount", 1.0) for succ in successors) or 1.0

            for succ in successors:
                edge_amt = self.graph[node][succ].get("amount", 1.0)
                # Proportional taint pass-through
                proportional_share = (edge_amt / total_out) * current_taint * decay
                
                existing = taint_scores.get(succ, 0.0)
                taint_scores[succ] = min(1.0, existing + proportional_share)

                frontier.append((succ, proportional_share, depth + 1))

        return taint_scores
