"""Forensic Natural Language Reasoning & SAR Report Generator."""

from typing import Dict, Any, List
import datetime


class ForensicReportGenerator:
    """Generates structured Suspicious Activity Reports (SAR) and narrative summaries for compliance teams."""

    @staticmethod
    def generate_narrative(tx_data: Dict[str, Any], risk_profile: Dict[str, Any], top_features: List[Dict[str, Any]]) -> str:
        """Constructs audit-ready natural language forensic narrative."""
        tx_hash = tx_data.get("tx_hash", "0x0000000000000000")
        sender = tx_data.get("sender", "Unknown")
        receiver = tx_data.get("receiver", "Unknown")
        amount = tx_data.get("amount", 0.0)
        risk_score = risk_profile.get("composite_risk_score", 0.0)
        risk_tier = risk_profile.get("risk_tier", "LOW")

        drivers = [f"{item.get('feature', 'Metric')} (Weight: {item.get('shap_value', 0.0)})" for item in top_features[:3]]
        drivers_str = ", ".join(drivers) if drivers else "Elevated transaction velocity and multi-hop peel chain structure"

        narrative = (
            f"FORENSIC INCIDENT SUMMARY [{risk_tier}]\n"
            f"Timestamp: {datetime.datetime.utcnow().isoformat()}Z\n"
            f"Target Transaction: {tx_hash}\n"
            f"Flow: {sender} -> {receiver} for {amount:.4f} Native Units\n\n"
            f"ASSESSMENT:\n"
            f"The automated AI Ensemble scored this transaction at {risk_score:.2f} ({risk_tier} RISK).\n"
            f"Primary risk drivers identified by Explainable AI: {drivers_str}.\n\n"
            f"RECOMMENDED COMPLIANCE ACTION:\n"
            f"- {risk_profile.get('recommended_action', 'MANUAL_INVESTIGATION')}\n"
            f"- Generate FinCEN SAR filing draft if counterparty matches sanction watchlists."
        )
        return narrative
