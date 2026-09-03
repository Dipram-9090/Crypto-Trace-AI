"""WebSocket Endpoint for Real-Time Streaming Alerts & Transactions."""

import asyncio
import json
import random
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("cryptotrace.backend.ws")
router = APIRouter(prefix="/ws", tags=["WebSockets"])


class ConnectionManager:
    """Manages active live WebSocket client connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """Streams simulated live on-chain scored transactions and high-severity fraud alerts to dashboard."""
    await manager.connect(websocket)
    try:
        while True:
            # Emit live transactions periodically
            await asyncio.sleep(3.0)
            is_anomaly = random.random() < 0.25
            risk_score = round(random.uniform(0.75, 0.98) if is_anomaly else random.uniform(0.01, 0.28), 4)

            feed_event = {
                "event_type": "HIGH_RISK_ALERT" if is_anomaly else "TRANSACTION_CLEARED",
                "tx_hash": "0x" + "".join(random.choices("0123456789abcdef", k=64)),
                "chain": random.choice(["Ethereum", "Bitcoin", "Polygon"]),
                "amount": round(random.uniform(0.1, 45.0), 4),
                "risk_score": risk_score,
                "tier": "CRITICAL" if risk_score > 0.8 else ("HIGH" if risk_score > 0.5 else "LOW"),
                "sender": "0x" + "".join(random.choices("0123456789abcdef", k=40)),
                "receiver": "0x" + "".join(random.choices("0123456789abcdef", k=40))
            }
            await websocket.send_text(json.dumps(feed_event))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WS error: {e}")
        manager.disconnect(websocket)
