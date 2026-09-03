"""API Routers module."""

from .routes_transactions import router as transactions_router
from .routes_wallets import router as wallets_router
from .routes_fraud import router as fraud_router
from .routes_ai import router as ai_router
from .routes_blockchain import router as blockchain_router
from .routes_auth import router as auth_router
from .routes_ws import router as ws_router

__all__ = [
    "transactions_router",
    "wallets_router",
    "fraud_router",
    "ai_router",
    "blockchain_router",
    "auth_router",
    "ws_router",
]
