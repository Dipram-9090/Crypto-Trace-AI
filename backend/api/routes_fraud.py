"""API Routes for Fraud Alerts and Investigation Triage."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.api_schemas import AlertCreateRequest, AlertResponse
from backend.services.alert_service import AlertService
from backend.authentication.auth_handler import get_current_user

router = APIRouter(prefix="/fraud", tags=["Fraud & Alerts"])
alert_service = AlertService()


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(limit: int = 50, user: dict = Depends(get_current_user)):
    """Retrieves active real-time suspicious activity alerts."""
    return alert_service.list_alerts(limit=limit)


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(payload: AlertCreateRequest, user: dict = Depends(get_current_user)):
    """Logs a new high-severity fraud alert for analyst triage."""
    return alert_service.create_alert(
        tx_hash=payload.tx_hash,
        severity=payload.severity,
        alert_type=payload.alert_type,
        description=payload.description
    )
