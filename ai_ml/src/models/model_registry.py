"""
Model Registry and Management

Tracks trained models, their metadata, performance metrics, and versioning.
Ensures reproducibility by storing:
- Model parameters
- Training configuration
- Feature list
- Preprocessing version
- Evaluation metrics
- Random seed
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import joblib

logger = logging.getLogger(__name__)


class ModelMetadata:
    """Stores and manages model metadata."""
    
    def __init__(
        self,
        model_name: str,
        version: str,
        model_type: str,
        training_dataset: str,
        feature_list: List[str],
        training_date: str = None,
        random_seed: int = 42,
        preprocessing_version: str = "v1.0",
        **kwargs
    ):
        """
        Initialize model metadata.
        
        Args:
            model_name: Name of the model
            version: Semantic version (e.g., "1.0.0")
            model_type: Type of model (e.g., "isolation_forest", "xgboost", "gnn")
            training_dataset: Name of training dataset
            feature_list: List of feature names used
            training_date: Training date (auto-populated if not provided)
            random_seed: Random seed for reproducibility
            preprocessing_version: Version of preprocessing pipeline
            **kwargs: Additional metadata
        """
        self.model_name = model_name
        self.version = version
        self.model_type = model_type
        self.training_dataset = training_dataset
        self.feature_list = feature_list
        self.training_date = training_date or datetime.now().isoformat()
        self.random_seed = random_seed
        self.preprocessing_version = preprocessing_version
        self.additional_metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "model_name": self.model_name,
            "version": self.version,
            "model_type": self.model_type,
            "training_dataset": self.training_dataset,
            "feature_list": self.feature_list,
            "training_date": self.training_date,
            "random_seed": self.random_seed,
            "preprocessing_version": self.preprocessing_version,
            **self.additional_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Create metadata from dictionary."""
        # Extract known fields
        known_fields = {
            "model_name", "version", "model_type", "training_dataset",
            "feature_list", "training_date", "random_seed", "preprocessing_version"
        }
        
        known = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        
        return cls(**known, **extra)


class ModelRegistry:
    """Central registry for trained models."""
    
    def __init__(self, registry_dir: str = "ai_ml/models"):
        """
        Initialize model registry.
        
        Args:
            registry_dir: Root directory for storing models
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.trained_dir = self.registry_dir / "trained"
        self.checkpoints_dir = self.registry_dir / "checkpoints"
        self.metadata_dir = self.registry_dir / "metadata"
        
        for d in [self.trained_dir, self.checkpoints_dir, self.metadata_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model registry initialized at {self.registry_dir}")
    
    def save_model(
        self,
        model: Any,
        model_name: str,
        metadata: ModelMetadata,
        format: str = "joblib"
    ) -> str:
        """
        Save trained model and metadata.
        
        Args:
            model: Trained model object
            model_name: Name for saving
            metadata: ModelMetadata instance
            format: Save format ("joblib" or "pickle")
        
        Returns:
            Path to saved model
        """
        # Save model
        if format == "joblib":
            model_path = self.trained_dir / f"{model_name}.joblib"
            joblib.dump(model, model_path)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        # Save metadata
        metadata_path = self.metadata_dir / f"{model_name}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        logger.info(f"Saved model: {model_path}")
        logger.info(f"Saved metadata: {metadata_path}")
        
        return str(model_path)
    
    def load_model(self, model_name: str, format: str = "joblib") -> tuple:
        """
        Load model and metadata.
        
        Args:
            model_name: Name of model to load
            format: Load format
        
        Returns:
            Tuple of (model, metadata)
        """
        # Load model
        if format == "joblib":
            model_path = self.trained_dir / f"{model_name}.joblib"
            model = joblib.load(model_path)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        # Load metadata
        metadata_path = self.metadata_dir / f"{model_name}_metadata.json"
        with open(metadata_path, "r") as f:
            metadata_dict = json.load(f)
        metadata = ModelMetadata.from_dict(metadata_dict)
        
        logger.info(f"Loaded model: {model_path}")
        return model, metadata
    
    def save_checkpoint(
        self,
        model: Any,
        checkpoint_name: str,
        epoch: int,
        metrics: Dict[str, float],
        format: str = "joblib"
    ) -> str:
        """
        Save training checkpoint.
        
        Args:
            model: Model state
            checkpoint_name: Checkpoint identifier
            epoch: Epoch number
            metrics: Training metrics at checkpoint
            format: Save format
        
        Returns:
            Path to checkpoint
        """
        checkpoint = {
            "model": model,
            "epoch": epoch,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_name}_epoch_{epoch}.joblib"
        joblib.dump(checkpoint, checkpoint_path)
        
        logger.info(f"Saved checkpoint: {checkpoint_path}")
        return str(checkpoint_path)
    
    def list_models(self) -> List[str]:
        """List all available trained models."""
        models = []
        for f in self.trained_dir.glob("*.joblib"):
            model_name = f.stem
            models.append(model_name)
        
        return sorted(models)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        metadata_path = self.metadata_dir / f"{model_name}_metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found for model: {model_name}")
        
        with open(metadata_path, "r") as f:
            metadata_dict = json.load(f)
        
        model_path = self.trained_dir / f"{model_name}.joblib"
        
        return {
            "name": model_name,
            "path": str(model_path),
            "exists": model_path.exists(),
            "metadata": metadata_dict,
            "file_size_mb": model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0
        }
    
    def delete_model(self, model_name: str) -> bool:
        """Delete model and its metadata."""
        model_path = self.trained_dir / f"{model_name}.joblib"
        metadata_path = self.metadata_dir / f"{model_name}_metadata.json"
        
        deleted = False
        
        if model_path.exists():
            model_path.unlink()
            deleted = True
            logger.info(f"Deleted model: {model_path}")
        
        if metadata_path.exists():
            metadata_path.unlink()
            logger.info(f"Deleted metadata: {metadata_path}")
        
        return deleted


class EvaluationMetrics:
    """Stores model evaluation metrics."""
    
    def __init__(
        self,
        model_name: str,
        dataset_name: str,
        **metrics
    ):
        """
        Initialize evaluation metrics.
        
        Args:
            model_name: Name of the model
            dataset_name: Name of evaluation dataset
            **metrics: Key-value pairs of metrics
        """
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.evaluation_date = datetime.now().isoformat()
        self.metrics = metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "model_name": self.model_name,
            "dataset_name": self.dataset_name,
            "evaluation_date": self.evaluation_date,
            "metrics": self.metrics
        }
    
    def save(self, filepath: str):
        """Save metrics to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved metrics to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> "EvaluationMetrics":
        """Load metrics from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        
        return cls(
            model_name=data["model_name"],
            dataset_name=data["dataset_name"],
            **data["metrics"]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    registry = ModelRegistry()
    
    # List all models
    print("Available models:")
    for model_name in registry.list_models():
        print(f"  - {model_name}")
        info = registry.get_model_info(model_name)
        print(f"    Version: {info['metadata'].get('version')}")
        print(f"    Type: {info['metadata'].get('model_type')}")
        print(f"    Size: {info['file_size_mb']:.2f} MB")
