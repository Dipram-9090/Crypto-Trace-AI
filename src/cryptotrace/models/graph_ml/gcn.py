"""
Graph Convolutional Network (GCN) Implementation.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class GCNLayer(nn.Module):
    def __init__(self, in_features: int, out_features: int):
        super(GCNLayer, self).__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        support = self.linear(x)
        return torch.matmul(adj_norm, support)


class GCNNet(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 64, out_channels: int = 2, dropout: float = 0.2):
        super(GCNNet, self).__init__()
        self.gc1 = GCNLayer(in_channels, hidden_channels)
        self.gc2 = GCNLayer(hidden_channels, out_channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.gc1(x, adj_norm))
        x = self.dropout(x)
        return self.gc2(x, adj_norm)
