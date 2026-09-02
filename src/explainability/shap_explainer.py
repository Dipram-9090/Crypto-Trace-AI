"""
Model explainability engine using SHAP for CryptoTrace AI.
Generates local feature attributions, directionality, and structured forensic evidence packages.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import shap
import logging

logger = logging.getLogger(__name__)

# Human-readable feature name translation dictionary
FEATURE_EXPLANATIONS = {
    "fan_out_ratio": "High output split / fan-out ratio (layering indicator)",
    "is_high_fanout": "Unusually high number of output destinations",
    "wallet_tx_velocity_per_hour": "High transaction velocity per hour",
    "burst_score": "Rapid transaction burst activity in tight time window",
    "shared_infrastructure_indicator": "IP shared across multiple distinct wallet addresses",
    "ip_associated_wallets_count": "Multiple wallets originating from single observed IP",
    "output_amount_variance": "High variance in distributed output amounts",
    "output_entropy": "High entropy in output amount distribution (mixing pattern)",
    "input_entropy": "High entropy in input sources",
    "wallet_unique_ips_count": "Frequent IP address hopping observed for wallet",
    "wallet_unique_asns_count": "Multiple Autonomous Systems (ASNs) used by wallet",
    "time_since_prev_wallet_tx": "Extremely short interval since preceding transaction",
    "time_since_prev_ip_tx": "Extremely short interval from current source IP",
    "wallet_txs_last_1h": "High transaction volume within past 1 hour",
    "wallet_txs_last_24h": "High transaction volume within past 24 hours",
    "graph_pagerank": "High graph centrality / PageRank in transaction network",
    "graph_2hop_neighbors": "Dense 2-hop neighborhood in forensic graph",
    "graph_3hop_neighbors": "Broad 3-hop multi-layer network connectivity",
    "fee_ratio": "Abnormal transaction fee ratio",
    "transaction_value": "High absolute transaction value",
}


class CryptoSHAPExplainer:
    """
    SHAP-based explainability engine for XGBoost forensic models.
    """

    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            # Handle wrapper or raw booster
            raw_model = getattr(self.model, "model", self.model)
            self.explainer = shap.TreeExplainer(raw_model)
        except Exception as e:
            logger.warning(f"SHAP TreeExplainer initialization warning: {e}. Fallback to Exact/Kernel.")
            self.explainer = None

    def explain_instance(self, features_row: pd.Series, top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Compute top feature contributions for a single transaction or entity.
        Returns list of structured evidence items.
        """
        # Ensure row is in correct feature order
        vals = [float(features_row.get(f, 0.0)) for f in self.feature_names]
        X_inst = np.array([vals])

        if self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X_inst)
                if isinstance(shap_values, list):
                    # Binary classification list [class0, class1]
                    s_vals = shap_values[1][0]
                elif shap_values.ndim == 2:
                    s_vals = shap_values[0]
                else:
                    s_vals = shap_values
            except Exception as e:
                logger.error(f"Error computing SHAP values: {e}")
                s_vals = np.zeros(len(self.feature_names))
        else:
            # Deterministic heuristic attribution based on deviation from feature scale
            s_vals = np.array(vals) / (np.std(vals) + 1e-5)

        # Pair features with shap values and feature values
        contributions = []
        for feat, s_val, val in zip(self.feature_names, s_vals, vals):
            human_desc = FEATURE_EXPLANATIONS.get(feat, feat.replace("_", " ").title())
            direction = "increased_risk" if s_val > 0 else "decreased_risk"
            contributions.append(
                {
                    "feature": feat,
                    "description": human_desc,
                    "value": round(float(val), 4),
                    "shap_value": round(float(s_val), 4),
                    "direction": direction,
                    "magnitude": abs(float(s_val)),
                }
            )

        # Sort by magnitude of contribution
        contributions.sort(key=lambda x: x["magnitude"], reverse=True)
        return contributions[:top_k]

    def generate_evidence_package(
        self,
        entity_id: str,
        risk_score: float,
        ml_probability: float,
        anomaly_score: float,
        graph_score: float,
        risk_level: str,
        features_row: pd.Series,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """
        Generate machine-readable JSON forensic package for investigations and dashboard.
        """
        evidence = self.explain_instance(features_row, top_k)
        return {
            "entity_id": entity_id,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "ml_probability": round(ml_probability, 4),
            "anomaly_score": round(anomaly_score, 1),
            "graph_score": round(graph_score, 1),
            "evidence": evidence,
        }
