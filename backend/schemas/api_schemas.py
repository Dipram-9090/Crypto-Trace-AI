"""Pydantic V2 Request and Response Validation Schemas."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# User & Auth
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    role: Optional[str] = "investigator"


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


# Transactions
class TransactionAnalysisRequest(BaseModel):
    tx_hash: str
    chain: Optional[str] = "ethereum"
    sender: Optional[str] = None
    receiver: Optional[str] = None
    amount: Optional[float] = 1.0


class TransactionAnalysisResponse(BaseModel):
    transaction_hash: str
    chain: str
    sender: str
    receiver: str
    amount: float
    risk_verdict: Dict[str, Any]
    explainability: Dict[str, Any]
    narrative_report: str


# Wallets
class WalletProfileRequest(BaseModel):
    address: str
    chain: Optional[str] = "ethereum"


class WalletProfileResponse(BaseModel):
    address: str
    chain: str
    risk_score: float
    risk_level: str
    is_sanctioned: bool
    sanction_metadata: Optional[Dict[str, Any]]
    total_received_eth: float
    total_sent_eth: float
    current_balance_eth: float
    transaction_count: int
    counterparty_summary: Dict[str, Any]


# Multi-Hop Graph
class MultiHopTraceRequest(BaseModel):
    start_address: str
    max_hops: Optional[int] = 3
    min_amount: Optional[float] = 0.0


class MultiHopTraceResponse(BaseModel):
    root_address: str
    total_hops: int
    unique_addresses_reached: int
    nodes: List[str]
    edges: List[Dict[str, Any]]


# Alerts
class AlertCreateRequest(BaseModel):
    tx_hash: str
    severity: str
    alert_type: str
    description: str


class AlertResponse(BaseModel):
    alert_id: str
    tx_hash: str
    severity: str
    alert_type: str
    description: str
    status: str
    created_at: datetime
