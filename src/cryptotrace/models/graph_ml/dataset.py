"""
Graph Dataset Builder and PyTorch Tensor Formatter.
"""
import torch
import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any


def build_graph_tensors(
    G: nx.DiGraph,
    node_list: List[str],
    features: np.ndarray,
    labels: np.ndarray
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Constructs normalized adjacency matrix and PyTorch tensors."""
    N = len(node_list)
    node_to_idx = {n: i for i, n in enumerate(node_list)}
    adj = np.zeros((N, N), dtype=np.float32)

    for u, v in G.edges():
        if u in node_to_idx and v in node_to_idx:
            i, j = node_to_idx[u], node_to_idx[v]
            adj[i, j] = 1.0
            adj[j, i] = 1.0

    np.fill_diagonal(adj, 1.0)
    row_sum = np.sum(adj, axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    adj_norm = adj / row_sum

    x = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)
    adj_tensor = torch.tensor(adj_norm, dtype=torch.float32)

    return x, y, adj_tensor
