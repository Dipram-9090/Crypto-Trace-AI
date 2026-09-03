"""
AI/ML Module - Complete Machine Learning Pipeline

This module provides:
- Data loading and validation
- Feature engineering
- Model training and evaluation
- Risk scoring and explainability
- Backend API integration
"""

__version__ = "1.0.0"
__author__ = "CryptoTrace AI Engineering Team"

from ai_ml.src.data.loaders import DataLoaderFactory, EllipticDataLoader, BitcoinHeistDataLoader
from ai_ml.src.data.validators import EllipticValidator, BitcoinHeistValidator
from ai_ml.src.inference.risk_scoring import RiskScorer, RiskLevel, RiskScoreResult
from ai_ml.src.models.model_registry import ModelRegistry, ModelMetadata

__all__ = [
    "DataLoaderFactory",
    "EllipticDataLoader",
    "BitcoinHeistDataLoader",
    "EllipticValidator",
    "BitcoinHeistValidator",
    "RiskScorer",
    "RiskLevel",
    "RiskScoreResult",
    "ModelRegistry",
    "ModelMetadata"
]
