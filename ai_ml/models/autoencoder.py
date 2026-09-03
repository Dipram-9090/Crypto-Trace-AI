"""Deep Autoencoder for Blockchain Anomaly Reconstruction Loss."""

import os
import logging
from typing import Optional
import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger("cryptotrace.ai_ml.models.autoencoder")


class PyTorchAutoencoder(nn.Module):
    """Deep Symmetrical Autoencoder (Bottleneck compression)."""

    def __init__(self, input_dim: int = 16, latent_dim: int = 4):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.BatchNorm1d(32),
            nn.LeakyReLU(0.1),
            nn.Linear(32, 16),
            nn.LeakyReLU(0.1),
            nn.Linear(16, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.LeakyReLU(0.1),
            nn.Linear(16, 32),
            nn.LeakyReLU(0.1),
            nn.Linear(32, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction


class TransactionAutoencoder:
    """Wrapper for training deep autoencoders and calculating sample-wise reconstruction error."""

    def __init__(self, input_dim: int = 16, latent_dim: int = 4, model_path: Optional[str] = None):
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = PyTorchAutoencoder(input_dim, latent_dim).to(self.device)
        self.threshold = 0.5

    def fit(self, X: np.ndarray, epochs: int = 30, batch_size: int = 64, lr: float = 0.001):
        """Trains autoencoder on normal baseline transaction distribution."""
        self.net.train()
        optimizer = torch.optim.Adam(self.net.parameters(), lr=lr, weight_decay=1e-5)
        criterion = nn.MSELoss()

        tensor_x = torch.FloatTensor(X)
        dataset = torch.utils.data.TensorDataset(tensor_x)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            total_loss = 0.0
            for (batch,) in loader:
                batch = batch.to(self.device)
                optimizer.zero_grad()
                recon = self.net(batch)
                loss = criterion(recon, batch)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(batch)

        # Compute 95th percentile reconstruction loss as anomaly threshold
        errors = self.get_reconstruction_error(X)
        self.threshold = float(np.percentile(errors, 95))
        logger.info(f"Autoencoder trained. Calibration threshold set to: {self.threshold:.4f}")

    def get_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        """Returns Mean Squared Reconstruction Error for each transaction vector."""
        self.net.eval()
        with torch.no_grad():
            tensor_x = torch.FloatTensor(X).to(self.device)
            recon = self.net(tensor_x)
            mse = torch.mean((tensor_x - recon) ** 2, dim=1)
            return mse.cpu().numpy()

    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """Calibrates reconstruction error into a normalized risk score [0, 1]."""
        errors = self.get_reconstruction_error(X)
        # Sigmoid compression relative to threshold
        scores = 1.0 / (1.0 + np.exp(-4 * (errors - self.threshold) / (self.threshold + 1e-5)))
        return scores
