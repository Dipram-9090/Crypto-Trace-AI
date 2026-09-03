"""
Example FastAPI Integration for CryptoTrace AI ML Pipeline

This example shows how to integrate the ML models with the existing FastAPI backend.
Add this to backend/main.py or create backend/routes/ml.py and include it.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_ml.src.models.model_registry import ModelRegistry
from ai_ml.src.api.ml_service import (
    MLServiceHandler,
    AnalysisRequest,
    AnalysisResponse,
    HealthCheckResponse
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/ml", tags=["ML Inference"])

# Initialize model registry and handler
try:
    model_registry = ModelRegistry("ai_ml/models")
    ml_handler = MLServiceHandler(model_registry)
    logger.info("ML Pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ML Pipeline: {str(e)}")
    ml_handler = None


# ============================================================================
# ML ANALYSIS ENDPOINT
# ============================================================================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transactions(request: AnalysisRequest):
    """
    Analyze transactions and return risk scores.
    
    This endpoint accepts either:
    1. A dataset file path (CSV/JSON)
    2. Inline transaction data
    
    Returns risk scores (0-100) and investigation leads.
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/ml/analyze" \
      -H "Content-Type: application/json" \
      -d '{
        "dataset_path": "data/transactions.csv",
        "model_name": "ensemble",
        "include_explanations": true
      }'
    ```
    """
    try:
        if ml_handler is None:
            raise HTTPException(
                status_code=503,
                detail="ML Pipeline not initialized"
            )
        
        # Call ML service
        response = await ml_handler.analyze_transactions(request)
        
        # Log analysis
        logger.info(
            f"Analyzed {response.records_analyzed} transactions, "
            f"found {response.high_risk_count} high-risk cases"
        )
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")


# ============================================================================
# MODEL MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/models")
async def list_models():
    """
    List all available trained models.
    
    Returns model names, types, versions, and performance metrics.
    
    Example:
    ```bash
    curl "http://localhost:8000/api/ml/models"
    ```
    """
    try:
        if ml_handler is None:
            raise HTTPException(status_code=503, detail="ML Pipeline not initialized")
        
        models = ml_handler.get_available_models()
        return {
            "status": "success",
            "count": len(models),
            "models": models,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """
    Get detailed information about a specific model.
    
    Returns metadata, metrics, and configuration.
    
    Example:
    ```bash
    curl "http://localhost:8000/api/ml/models/elliptic_ensemble"
    ```
    """
    try:
        if ml_handler is None:
            raise HTTPException(status_code=503, detail="ML Pipeline not initialized")
        
        info = model_registry.get_model_info(model_name)
        
        if not info.get("exists"):
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        return {
            "status": "success",
            "model": info,
            "timestamp": datetime.now().isoformat()
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model info")


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check for ML pipeline.
    
    Returns service status and number of available models.
    
    Example:
    ```bash
    curl "http://localhost:8000/api/ml/health"
    ```
    """
    try:
        if ml_handler is None:
            return HealthCheckResponse(
                status="unhealthy",
                models_available=0,
                timestamp=datetime.now().isoformat(),
                message="ML Pipeline not initialized"
            )
        
        return ml_handler.health_check()
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            models_available=0,
            timestamp=datetime.now().isoformat(),
            message=f"Error: {str(e)}"
        )


@router.get("/status")
async def status():
    """
    Detailed status endpoint.
    
    Returns comprehensive system status.
    """
    try:
        models = model_registry.list_models() if model_registry else []
        
        return {
            "status": "operational" if models else "degraded",
            "components": {
                "data_layer": "available",
                "models": {
                    "count": len(models),
                    "available": models
                },
                "inference": "available" if ml_handler else "unavailable",
                "api": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# BATCH INFERENCE ENDPOINTS
# ============================================================================

@router.post("/batch/analyze")
async def batch_analyze(
    file_path: str = Query(..., description="Path to CSV/JSON file"),
    model_name: str = Query("ensemble", description="Model to use"),
    chunk_size: int = Query(10000, description="Batch chunk size")
):
    """
    Analyze large batch of transactions.
    
    Processes file in chunks to manage memory efficiently.
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/ml/batch/analyze" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "file_path=data/large_batch.csv&model_name=ensemble&chunk_size=10000"
    ```
    """
    try:
        import pandas as pd
        
        if ml_handler is None:
            raise HTTPException(status_code=503, detail="ML Pipeline not initialized")
        
        # Check file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Load model
        try:
            model, metadata = model_registry.load_model(model_name)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        # Process in chunks
        results = []
        total_analyzed = 0
        high_risk_count = 0
        risk_scores = []
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            # Convert chunk to transactions
            from ai_ml.src.api.ml_service import TransactionInput
            
            transactions = [
                TransactionInput(
                    transaction_id=row.get("transaction_id", str(i)),
                    features=row.to_dict()
                )
                for i, row in chunk.iterrows()
            ]
            
            # Create request for this chunk
            chunk_request = AnalysisRequest(
                transactions=transactions,
                model_name=model_name,
                include_explanations=True
            )
            
            # Analyze chunk
            chunk_response = await ml_handler.analyze_transactions(chunk_request)
            
            results.extend(chunk_response.results)
            total_analyzed += chunk_response.records_analyzed
            high_risk_count += chunk_response.high_risk_count
            risk_scores.extend([r.risk_score for r in chunk_response.results])
        
        avg_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "status": "success",
            "total_records": total_analyzed,
            "high_risk_count": high_risk_count,
            "average_risk_score": avg_score,
            "top_results": sorted(results, key=lambda x: x.risk_score, reverse=True)[:100],
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch analysis failed")


# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

def include_ml_routes(app):
    """
    Include ML routes in FastAPI app.
    
    Usage in main.py:
    ```python
    from fastapi import FastAPI
    from backend.routes.ml import include_ml_routes
    
    app = FastAPI()
    include_ml_routes(app)
    ```
    """
    app.include_router(router)
    logger.info("ML routes included in FastAPI app")


# Example FastAPI application setup
if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn
    
    # Create app
    app = FastAPI(title="CryptoTrace AI ML Pipeline", version="1.0.0")
    
    # Include ML routes
    include_ml_routes(app)
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
