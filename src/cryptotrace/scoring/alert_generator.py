"""
Investigative Alert Generator & Machine-Readable Evidence Builder.
"""
from typing import Dict, Any, List
import pandas as pd


class AlertGenerator:
    """Formats forensic dossiers and generates prioritized alert objects."""
    @staticmethod
    def create_alert(
        alert_idx: int,
        row: pd.Series,
        composite_score: float,
        risk_level: str,
        confidence: float,
        top_factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return {
            "alert_id": f"ALERT_{alert_idx:04d}",
            "txid": str(row.get("txid")),
            "primary_wallet": str(row.get("primary_wallet", "N/A")),
            "risk_score": composite_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "ml_probability": round(float(row.get("ml_probability", 0.0)), 4),
            "anomaly_score": round(float(row.get("anomaly_score", 0.0)), 1),
            "graph_score": round(float(row.get("graph_score", 0.0)), 1),
            "src_ip": str(row.get("src_ip", "N/A")),
            "src_country": str(row.get("src_country", "N/A")),
            "src_asn": str(row.get("src_asn", "N/A")),
            "timestamp": str(row.get("timestamp", "N/A")),
            "top_features": top_factors
        }
