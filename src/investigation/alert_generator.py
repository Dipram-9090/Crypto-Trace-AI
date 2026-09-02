"""
Investigative Lead and Ranked Alert Generation Engine for CryptoTrace AI.
Synthesizes multi-model predictions and graph intelligence into actionable forensic alerts.
"""

from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ForensicAlert:
    alert_id: str
    entity_type: str
    entity_id: str
    risk_score: float
    risk_level: str
    ml_probability: float
    anomaly_score: float
    graph_score: float
    top_features: List[Dict[str, Any]]
    related_transactions: List[str]
    related_wallets: List[str]
    related_ips: List[str]
    related_asns: List[str]
    timestamp: str
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "ml_probability": self.ml_probability,
            "anomaly_score": self.anomaly_score,
            "graph_score": self.graph_score,
            "top_features": self.top_features,
            "related_transactions": self.related_transactions,
            "related_wallets": self.related_wallets,
            "related_ips": self.related_ips,
            "related_asns": self.related_asns,
            "timestamp": self.timestamp,
            "explanation": self.explanation,
        }


class AlertGenerator:
    """
    Generates and filters ranked forensic alerts from processed transactions and predictions.
    """

    def __init__(self, min_risk_threshold: float = 30.0):
        self.min_risk_threshold = min_risk_threshold

    def generate_alerts(
        self, scored_df: pd.DataFrame, evidence_dict: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ) -> List[ForensicAlert]:
        """
        Generate ranked alert list from scored DataFrame.
        """
        if scored_df.empty:
            return []

        # Sort descending by composite risk score
        sorted_df = scored_df.sort_values("composite_risk_score", ascending=False).reset_index(drop=True)
        alerts: List[ForensicAlert] = []

        for idx, row in sorted_df.iterrows():
            score = float(row.get("composite_risk_score", 0.0))
            if score < self.min_risk_threshold:
                continue

            alert_num = len(alerts) + 1
            alert_id = f"ALERT_{alert_num:04d}"
            txid = str(row.get("txid", ""))
            primary_wallet = str(row.get("primary_wallet", ""))
            entity_id = primary_wallet if primary_wallet else txid

            src_ip = str(row.get("src_ip", ""))
            src_asn = str(row.get("src_asn", ""))
            ts = str(row.get("timestamp", ""))
            risk_level = str(row.get("risk_level", "LOW"))
            ml_prob = float(row.get("ml_probability", 0.0))
            anom_score = float(row.get("anomaly_score", 0.0))
            graph_score = float(row.get("graph_score", 0.0))

            evidence_items = evidence_dict.get(txid, []) if evidence_dict else []

            # Construct summary narrative
            reasons = [e.get("description", e.get("feature", "")) for e in evidence_items[:3]]
            reason_str = "; ".join(reasons) if reasons else "Multi-modal model anomaly detection"

            alert = ForensicAlert(
                alert_id=alert_id,
                entity_type="Wallet" if primary_wallet else "Transaction",
                entity_id=entity_id,
                risk_score=round(score, 1),
                risk_level=risk_level,
                ml_probability=round(ml_prob, 4),
                anomaly_score=round(anom_score, 1),
                graph_score=round(graph_score, 1),
                top_features=evidence_items,
                related_transactions=[txid],
                related_wallets=[primary_wallet] if primary_wallet else [],
                related_ips=[src_ip] if src_ip else [],
                related_asns=[src_asn] if src_asn else [],
                timestamp=ts,
                explanation=f"Flagged with {risk_level} priority: {reason_str}",
            )
            alerts.append(alert)

        logger.info(f"Generated {len(alerts)} ranked forensic alerts.")
        return alerts

    def filter_alerts(
        self, alerts: List[ForensicAlert], risk_level: Optional[str] = None, search_query: Optional[str] = None
    ) -> List[ForensicAlert]:
        """Filter alerts by risk tier or text search in entity IDs/IPs/ASNs."""
        res = alerts
        if risk_level and risk_level != "ALL":
            res = [a for a in res if a.risk_level.upper() == risk_level.upper()]

        if search_query and search_query.strip():
            q = search_query.strip().lower()
            res = [
                a
                for a in res
                if (
                    q in a.alert_id.lower()
                    or q in a.entity_id.lower()
                    or any(q in w.lower() for w in a.related_wallets)
                    or any(q in ip.lower() for ip in a.related_ips)
                    or any(q in asn.lower() for asn in a.related_asns)
                )
            ]
        return res
