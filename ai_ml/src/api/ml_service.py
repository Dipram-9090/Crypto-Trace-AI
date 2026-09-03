"""
Backend API Integration for ML Models

REST API endpoints for model inference and analysis.
Integrates with the existing FastAPI backend.

Endpoints:
- POST /api/ml/analyze - Analyze transactions and get risk scores
- GET /api/ml/models - List available models
- GET /api/ml/status - Health check
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RiskLevelEnum(str, Enum):
    """Risk level categories."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TransactionInput(BaseModel):
    """Input transaction for analysis."""
    
    transaction_id: str = Field(..., description="Unique transaction identifier")
    features: Dict[str, float] = Field(..., description="Transaction feature vector")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TX123456",
                "features": {
                    "feature_0": 0.5,
                    "feature_1": 0.8,
                    "feature_2": 0.3
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class RiskScoreResponse(BaseModel):
    """Risk score for a single transaction."""
    
    transaction_id: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    risk_level: RiskLevelEnum
    anomaly_score: Optional[float] = None
    classification_probability: Optional[float] = None
    model_version: str = Field(default="v1.0", description="Model version used")
    top_features: List[str] = Field(default=[], description="Top contributing features")
    investigation_signals: List[str] = Field(default=[], description="Investigation signals")
    confidence: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TX123456",
                "risk_score": 82,
                "risk_level": "HIGH",
                "anomaly_score": 0.78,
                "model_version": "ensemble_v1.0",
                "top_features": ["fund_dispersion", "transaction_velocity"],
                "investigation_signals": [
                    "High transaction velocity",
                    "Fund dispersion pattern detected"
                ],
                "confidence": 0.92
            }
        }


class AnalysisRequest(BaseModel):
    """Batch analysis request."""
    
    dataset_path: Optional[str] = Field(None, description="Path to input dataset (CSV/JSON)")
    transactions: Optional[List[TransactionInput]] = Field(None, description="Inline transactions")
    model_name: str = Field("ensemble", description="Model to use for inference")
    include_explanations: bool = Field(True, description="Include feature explanations")
    
    class Config:
        schema_extra = {
            "example": {
                "dataset_path": "data/transactions.csv",
                "model_name": "ensemble",
                "include_explanations": True
            }
        }


class AnalysisResponse(BaseModel):
    """Analysis response."""
    
    status: str = Field("success", description="Response status")
    records_analyzed: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    average_risk_score: float
    results: List[RiskScoreResponse]
    timestamp: str = Field(description="Analysis timestamp")
    message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "records_analyzed": 1000,
                "high_risk_count": 23,
                "moderate_risk_count": 45,
                "low_risk_count": 932,
                "average_risk_score": 28.5,
                "results": [],
                "timestamp": "2024-01-15T11:45:00Z"
            }
        }


class ModelInfo(BaseModel):
    """Information about a trained model."""
    
    model_name: str
    model_type: str
    version: str
    training_dataset: str
    evaluation_metrics: Dict[str, Any]
    feature_count: int
    training_date: str
    
    class Config:
        schema_extra = {
            "example": {
                "model_name": "elliptic_ensemble",
                "model_type": "ensemble",
                "version": "1.0.0",
                "training_dataset": "elliptic",
                "evaluation_metrics": {
                    "precision": 0.92,
                    "recall": 0.87,
                    "f1": 0.89,
                    "roc_auc": 0.98
                },
                "feature_count": 166,
                "training_date": "2024-01-01T10:00:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field("healthy", description="Service status")
    models_available: int
    timestamp: str
    message: Optional[str] = None


# ============================================================================
# API ROUTE DEFINITIONS (For FastAPI Integration)
# ============================================================================

API_ROUTES = {
    "analyze": {
        "path": "/api/ml/analyze",
        "methods": ["POST"],
        "description": "Analyze transactions and return risk scores",
        "request_model": AnalysisRequest,
        "response_model": AnalysisResponse
    },
    "models": {
        "path": "/api/ml/models",
        "methods": ["GET"],
        "description": "List available models",
        "response_model": List[ModelInfo]
    },
    "model_details": {
        "path": "/api/ml/models/{model_name}",
        "methods": ["GET"],
        "description": "Get details for a specific model",
        "response_model": ModelInfo
    },
    "health": {
        "path": "/api/ml/health",
        "methods": ["GET"],
        "description": "Health check endpoint",
        "response_model": HealthCheckResponse
    }
}


# ============================================================================
# ML SERVICE HANDLER (Integration Logic)
# ============================================================================

class MLServiceHandler:
    """Handles ML model inference requests."""
    
    def __init__(self, model_registry, model_loader=None):
        """
        Initialize ML service handler.
        
        Args:
            model_registry: ModelRegistry instance
            model_loader: Optional custom model loader
        """
        self.model_registry = model_registry
        self.model_loader = model_loader
        self.logger = logging.getLogger(__name__)
    
    async def analyze_transactions(
        self,
        request: AnalysisRequest
    ) -> AnalysisResponse:
        """
        Analyze transactions using the specified model.
        
        Args:
            request: Analysis request
        
        Returns:
            Analysis response with risk scores
        
        Raises:
            ValueError: If model not found or input invalid
        """
        try:
            # Load data (CSV, JSON, or inline)
            if request.dataset_path:
                import pandas as pd
                df = pd.read_csv(request.dataset_path)
                transactions = [
                    TransactionInput(
                        transaction_id=row.get("transaction_id", str(i)),
                        features=row.to_dict()
                    )
                    for i, row in df.iterrows()
                ]
            else:
                transactions = request.transactions or []
            
            if not transactions:
                raise ValueError("No transactions provided")
            
            # Load model
            model_name = request.model_name
            try:
                model, metadata = self.model_registry.load_model(model_name)
            except Exception as e:
                self.logger.error(f"Failed to load model {model_name}: {str(e)}")
                raise ValueError(f"Model '{model_name}' not found or failed to load")
            
            # Run inference
            results = []
            risk_scores = []
            
            for tx in transactions:
                try:
                    # Get predictions from model
                    feature_vector = list(tx.features.values())
                    
                    # Model-specific prediction logic
                    if hasattr(model, 'predict_proba'):
                        # Classifier
                        proba = model.predict_proba([feature_vector])[0]
                        risk_score = int(proba[1] * 100)
                    elif hasattr(model, 'decision_function'):
                        # SVM/anomaly detector
                        score = model.decision_function([feature_vector])[0]
                        risk_score = int((score + 1) / 2 * 100)  # Normalize to 0-100
                    else:
                        # Default: use direct output
                        pred = model.predict([feature_vector])[0]
                        risk_score = int(pred * 100)
                    
                    risk_score = max(0, min(100, risk_score))  # Clip to 0-100
                    
                    # Determine risk level
                    if risk_score <= 20:
                        risk_level = RiskLevelEnum.LOW
                    elif risk_score <= 40:
                        risk_level = RiskLevelEnum.MODERATE
                    elif risk_score <= 60:
                        risk_level = RiskLevelEnum.ELEVATED
                    elif risk_score <= 80:
                        risk_level = RiskLevelEnum.HIGH
                    else:
                        risk_level = RiskLevelEnum.CRITICAL
                    
                    # Generate signals (simplified)
                    signals = []
                    if risk_score >= 80:
                        signals.append("Extremely anomalous behavior")
                    if risk_score >= 60:
                        signals.append("Anomalous pattern detected")
                    
                    result = RiskScoreResponse(
                        transaction_id=tx.transaction_id,
                        risk_score=risk_score,
                        risk_level=risk_level,
                        model_version=metadata.version,
                        investigation_signals=signals,
                        confidence=0.85
                    )
                    
                    results.append(result)
                    risk_scores.append(risk_score)
                
                except Exception as e:
                    self.logger.error(f"Error analyzing {tx.transaction_id}: {str(e)}")
                    continue
            
            # Aggregate results
            from datetime import datetime
            
            high_risk = sum(1 for s in risk_scores if s >= 60)
            moderate_risk = sum(1 for s in risk_scores if 40 <= s < 60)
            low_risk = sum(1 for s in risk_scores if s < 40)
            avg_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            return AnalysisResponse(
                status="success",
                records_analyzed=len(transactions),
                high_risk_count=high_risk,
                moderate_risk_count=moderate_risk,
                low_risk_count=low_risk,
                average_risk_score=avg_score,
                results=results,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return AnalysisResponse(
                status="error",
                records_analyzed=0,
                high_risk_count=0,
                moderate_risk_count=0,
                low_risk_count=0,
                average_risk_score=0,
                results=[],
                timestamp=datetime.now().isoformat(),
                message=f"Analysis failed: {str(e)}"
            )
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models."""
        models = []
        
        for model_name in self.model_registry.list_models():
            try:
                info = self.model_registry.get_model_info(model_name)
                metadata = info["metadata"]
                
                models.append(ModelInfo(
                    model_name=model_name,
                    model_type=metadata.get("model_type", "unknown"),
                    version=metadata.get("version", "unknown"),
                    training_dataset=metadata.get("training_dataset", "unknown"),
                    evaluation_metrics=metadata.get("metrics", {}),
                    feature_count=len(metadata.get("feature_list", [])),
                    training_date=metadata.get("training_date", "unknown")
                ))
            except Exception as e:
                self.logger.warning(f"Error loading model {model_name}: {str(e)}")
        
        return models
    
    def health_check(self) -> HealthCheckResponse:
        """Check service health."""
        models_available = len(self.model_registry.list_models())
        
        return HealthCheckResponse(
            status="healthy" if models_available > 0 else "degraded",
            models_available=models_available,
            timestamp=datetime.now().isoformat(),
            message=f"{models_available} models available" if models_available > 0 else "No models loaded"
        )


if __name__ == "__main__":
    # Print API documentation
    print("\n" + "=" * 70)
    print("ML API DOCUMENTATION")
    print("=" * 70 + "\n")
    
    for route_name, route_info in API_ROUTES.items():
        print(f"[{route_info['methods'][0]}] {route_info['path']}")
        print(f"  Description: {route_info['description']}")
        if "request_model" in route_info:
            print(f"  Request: {route_info['request_model'].__name__}")
        print(f"  Response: {route_info['response_model'].__name__}")
        print()
