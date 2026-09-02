"""
Graph Neural Network (GraphSAGE) model for CryptoTrace AI.
Learns structural entity embeddings and classifies transaction nodes using neighborhood aggregation.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SAGEConvLayer(nn.Module):
    """
    Standard GraphSAGE Mean Aggregator Convolution layer.
    """
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super(SAGEConvLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.linear_self = nn.Linear(in_features, out_features, bias=bias)
        self.linear_neigh = nn.Linear(in_features, out_features, bias=False)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        # Aggregation: neigh_feats = adj_norm * x
        neigh = torch.spmm(adj_norm, x) if adj_norm.is_sparse else torch.matmul(adj_norm, x)
        out = self.linear_self(x) + self.linear_neigh(neigh)
        return out


class GraphSAGENet(nn.Module):
    """
    2-Layer GraphSAGE Network with Dropout and ReLU non-linearity.
    """
    def __init__(self, in_channels: int, hidden_channels: int = 64, out_channels: int = 2, dropout: float = 0.2):
        super(GraphSAGENet, self).__init__()
        self.conv1 = SAGEConvLayer(in_channels, hidden_channels)
        self.conv2 = SAGEConvLayer(hidden_channels, out_channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        h = self.conv1(x, adj_norm)
        h = F.relu(h)
        h = self.dropout(h)
        out = self.conv2(h, adj_norm)
        return out


class CryptoGraphSAGE:
    """
    Forensic Graph Neural Network training and inference manager.
    """
    def __init__(
        self,
        in_channels: int = 16,
        hidden_channels: int = 64,
        out_channels: int = 2,
        lr: float = 0.005,
        epochs: int = 40,
        dropout: float = 0.2
    ):
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.lr = lr
        self.epochs = epochs
        self.dropout = dropout
        self.model = None
        self.is_trained = False

    def _build_adj_matrix(self, G: nx.DiGraph, node_list: List[str]) -> torch.Tensor:
        """Create normalized symmetric adjacency matrix with self-loops."""
        node_to_idx = {n: i for i, n in enumerate(node_list)}
        N = len(node_list)
        adj = np.zeros((N, N), dtype=np.float32)

        for u, v in G.edges():
            if u in node_to_idx and v in node_to_idx:
                i, j = node_to_idx[u], node_to_idx[v]
                adj[i, j] = 1.0
                adj[j, i] = 1.0  # Undirected message passing for neighborhood context

        # Add self loops
        np.fill_diagonal(adj, 1.0)

        # Degree normalization: D^-1 * A
        row_sum = np.sum(adj, axis=1, keepdims=True)
        row_sum[row_sum == 0] = 1.0
        adj_norm = adj / row_sum

        return torch.tensor(adj_norm, dtype=torch.float32)

    def train(
        self,
        G: nx.DiGraph,
        node_list: List[str],
        features: np.ndarray,
        labels: np.ndarray,
        train_mask: np.ndarray,
        val_mask: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Train GraphSAGE model on node classification task."""
        num_features = features.shape[1]
        self.in_channels = num_features
        self.model = GraphSAGENet(self.in_channels, self.hidden_channels, self.out_channels, self.dropout)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=5e-4)
        criterion = nn.CrossEntropyLoss()

        x = torch.tensor(features, dtype=torch.float32)
        y = torch.tensor(labels, dtype=torch.long)
        adj_norm = self._build_adj_matrix(G, node_list)

        t_mask = torch.tensor(train_mask, dtype=torch.bool)
        v_mask = torch.tensor(val_mask, dtype=torch.bool) if val_mask is not None else None

        self.model.train()
        for epoch in range(self.epochs):
            optimizer.zero_grad()
            logits = self.model(x, adj_norm)
            loss = criterion(logits[t_mask], y[t_mask])
            loss.backward()
            optimizer.step()

        self.is_trained = True
        self.model.eval()
        with torch.no_grad():
            final_logits = self.model(x, adj_norm)
            probs = F.softmax(final_logits, dim=1)[:, 1].numpy()

        report = {
            "final_loss": float(loss.item()),
            "mean_gnn_prob": float(np.mean(probs)),
            "max_gnn_prob": float(np.max(probs))
        }
        logger.info(f"GraphSAGE training complete: {report}")
        return report

    def predict_proba(self, G: nx.DiGraph, node_list: List[str], features: np.ndarray) -> np.ndarray:
        """Predict suspiciousness probability for each node in node_list."""
        if not self.is_trained or self.model is None:
            # Return baseline probability if not trained
            return np.zeros(len(node_list), dtype=np.float32)

        self.model.eval()
        x = torch.tensor(features, dtype=torch.float32)
        adj_norm = self._build_adj_matrix(G, node_list)

        with torch.no_grad():
            logits = self.model(x, adj_norm)
            probs = F.softmax(logits, dim=1)[:, 1].numpy()
        return probs

    def save(self, filepath: str):
        if self.model is not None:
            torch.save({
                "state_dict": self.model.state_dict(),
                "in_channels": self.in_channels,
                "hidden_channels": self.hidden_channels,
                "out_channels": self.out_channels,
                "dropout": self.dropout
            }, filepath)
            logger.info(f"Saved GraphSAGE model to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "CryptoGraphSAGE":
        ckpt = torch.load(filepath, map_location="cpu")
        obj = cls(
            in_channels=ckpt["in_channels"],
            hidden_channels=ckpt["hidden_channels"],
            out_channels=ckpt["out_channels"],
            dropout=ckpt["dropout"]
        )
        obj.model = GraphSAGENet(obj.in_channels, obj.hidden_channels, obj.out_channels, obj.dropout)
        obj.model.load_state_dict(ckpt["state_dict"])
        obj.model.eval()
        obj.is_trained = True
        return obj
