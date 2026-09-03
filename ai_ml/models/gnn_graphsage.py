"""Graph Neural Network (GraphSAGE) for Blockchain Node / Transaction Risk Classification."""

import os
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("cryptotrace.ai_ml.models.gnn")


class GraphSAGEConv(nn.Module):
    """Mean-pooling GraphSAGE convolution layer implemented in pure PyTorch."""

    def __init__(self, in_feats: int, out_feats: int):
        super().__init__()
        self.linear_self = nn.Linear(in_feats, out_feats, bias=False)
        self.linear_neigh = nn.Linear(in_feats, out_feats, bias=True)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        """Args:
            x: Node features [N, in_feats]
            adj_norm: Normalized adjacency matrix [N, N]
        """
        neigh_feat = torch.matmul(adj_norm, x)
        h = self.linear_self(x) + self.linear_neigh(neigh_feat)
        return F.relu(h)


class GraphSAGENet(nn.Module):
    """2-Layer GraphSAGE Deep Architecture with Dropout and Sigmoid Risk Head."""

    def __init__(self, in_feats: int = 32, hidden_dim: int = 64, out_dim: int = 1, dropout: float = 0.2):
        super().__init__()
        self.conv1 = GraphSAGEConv(in_feats, hidden_dim)
        self.conv2 = GraphSAGEConv(hidden_dim, hidden_dim // 2)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim // 2, out_dim)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        h = self.conv1(x, adj)
        h = self.dropout(h)
        h = self.conv2(h, adj)
        h = self.dropout(h)
        logits = self.classifier(h)
        return torch.sigmoid(logits)


class GraphSAGETxClassifier:
    """Wrapper for training, embedding generation, and GNN inference."""

    def __init__(self, in_feats: int = 32, model_path: Optional[str] = "ml-models/graphsage/graphsage.pt"):
        self.in_feats = in_feats
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = GraphSAGENet(in_feats=in_feats).to(self.device)
        self._load_weights()

    def _load_weights(self):
        if self.model_path and os.path.exists(self.model_path):
            try:
                state = torch.load(self.model_path, map_location=self.device, weights_only=False)
                if isinstance(state, dict) and "state_dict" in state:
                    self.model.load_state_dict(state["state_dict"])
                elif isinstance(state, nn.Module):
                    self.model = state.to(self.device)
                logger.info(f"Loaded GraphSAGE model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load GNN weights: {e}. Model initialized with random weights.")

    def forward_scores(self, x_np: np.ndarray, adj_np: np.ndarray) -> np.ndarray:
        """Runs GNN inference over feature matrix and adjacency matrix."""
        self.model.eval()
        with torch.no_grad():
            x_t = torch.FloatTensor(x_np).to(self.device)
            # Row-normalize adjacency
            row_sum = adj_np.sum(axis=1, keepdims=True) + 1e-6
            adj_norm = adj_np / row_sum
            adj_t = torch.FloatTensor(adj_norm).to(self.device)

            probs = self.model(x_t, adj_t)
            return probs.cpu().numpy().flatten()
