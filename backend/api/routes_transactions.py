"""API Routes for Blockchain Transactions."""

from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.api_schemas import TransactionAnalysisRequest, TransactionAnalysisResponse
from backend.services.transaction_service import TransactionService
from backend.authentication.auth_handler import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])
tx_service = TransactionService()


@router.post("/analyze", response_model=TransactionAnalysisResponse)
async def analyze_transaction(payload: TransactionAnalysisRequest, user: dict = Depends(get_current_user)):
    """Analyzes a transaction hash using multi-model AI forensic evaluation."""
    try:
        verdict = tx_service.analyze_transaction(payload.tx_hash, payload.chain or "ethereum")
        return verdict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
