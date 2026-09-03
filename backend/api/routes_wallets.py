"""API Routes for Wallets & Graph Forensics."""

from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.api_schemas import WalletProfileRequest, WalletProfileResponse, MultiHopTraceRequest, MultiHopTraceResponse
from backend.services.wallet_service import WalletService
from backend.authentication.auth_handler import get_current_user

router = APIRouter(prefix="/wallets", tags=["Wallets"])
wallet_service = WalletService()


@router.post("/profile", response_model=WalletProfileResponse)
async def get_wallet_profile(payload: WalletProfileRequest, user: dict = Depends(get_current_user)):
    """Fetches risk profile, sanction status, balance, and counterparty metrics for an address."""
    try:
        profile = wallet_service.get_wallet_profile(payload.address, payload.chain or "ethereum")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trace", response_model=MultiHopTraceResponse)
async def trace_multihop(payload: MultiHopTraceRequest, user: dict = Depends(get_current_user)):
    """Performs forward multi-hop graph taint tracing from a starting suspect address."""
    try:
        res = wallet_service.trace_multihop(payload.start_address, payload.max_hops or 3, payload.min_amount or 0.0)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
