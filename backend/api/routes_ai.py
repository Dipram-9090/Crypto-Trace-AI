"""API Routes for AI Model Metadata & Benchmarks."""

from fastapi import APIRouter, Depends
from backend.services.ai_service import AIService
from backend.authentication.auth_handler import get_current_user

router = APIRouter(prefix="/ai", tags=["AI & Machine Learning"])
ai_service = AIService()


@router.get("/benchmarks")
async def get_benchmarks(user: dict = Depends(get_current_user)):
    """Returns model performance metrics (F1, ROC-AUC, latency) and ensemble weights."""
    return ai_service.get_model_benchmarks()
