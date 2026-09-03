"""Alert Management and Suspicious Activity Triage Service."""

from typing import Dict, Any, List
import datetime
import uuid


class AlertService:
    """Manages real-time fraud alerts and investigation tickets."""

    def __init__(self):
        self._mock_alerts = [
            {
                "alert_id": "ALT-8091",
                "tx_hash": "0x4a9b7c8d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b",
                "severity": "CRITICAL",
                "alert_type": "SANCTION_INTERACTION",
                "description": "Direct interaction with OFAC-sanctioned Lazarus Group bridge exploit address.",
                "status": "OPEN",
                "created_at": datetime.datetime.utcnow().isoformat()
            },
            {
                "alert_id": "ALT-8092",
                "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "severity": "HIGH",
                "alert_type": "PEELING_CHAIN",
                "description": "Multi-hop structuring detected: 10 consecutive peel hops with identical 0.1 BTC splits.",
                "status": "INVESTIGATING",
                "created_at": (datetime.datetime.utcnow() - datetime.timedelta(minutes=15)).isoformat()
            },
            {
                "alert_id": "ALT-8093",
                "tx_hash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
                "severity": "MEDIUM",
                "alert_type": "VELOCITY_SPIKE",
                "description": "Address generated 45 transactions in under 2 minutes (exceeds 99.5th percentile baseline).",
                "status": "OPEN",
                "created_at": (datetime.datetime.utcnow() - datetime.timedelta(minutes=45)).isoformat()
            }
        ]

    def list_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._mock_alerts[:limit]

    def create_alert(self, tx_hash: str, severity: str, alert_type: str, description: str) -> Dict[str, Any]:
        new_alert = {
            "alert_id": f"ALT-{uuid.uuid4().hex[:6].upper()}",
            "tx_hash": tx_hash,
            "severity": severity,
            "alert_type": alert_type,
            "description": description,
            "status": "OPEN",
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        self._mock_alerts.insert(0, new_alert)
        return new_alert
