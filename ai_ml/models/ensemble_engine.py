"""Forensic Ensemble Risk Engine combining XGBoost, GNN, Anomaly Detection, and Heuristics."""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger("cryptotrace.ai_ml.models.ensemble")


class ForensicEnsembleScorer:
    """Ensemble model blending supervised XGBoost classification, GraphSAGE topological embeddings, and Isolation Forest/Autoencoder anomaly metrics."""

    def __init__(
        self,
        weight_xgb: float = 0.40,
        weight_gnn: float = 0.30,
        weight_anomaly: float = 0.20,
        weight_heuristics: float = 0.10
    ):
        self.w_xgb = weight_xgb
        self.w_gnn = weight_gnn
        self.w_anomaly = weight_anomaly
        self.w_heuristics = weight_heuristics

    def compute_composite_risk(
        self,
        xgb_score: float,
        gnn_score: float,
        anomaly_score: float,
        heuristic_score: float = 0.0
    ) -> Dict[str, Any]:
        """Calculates normalized composite risk score and maps to categorical tier."""
        composite = (
            self.w_xgb * xgb_score +
            self.w_gnn * gnn_score +
            self.w_anomaly * anomaly_score +
            self.w_heuristics * heuristic_score
        )
        composite = float(np.clip(composite, 0.0, 1.0))

        if composite >= 0.75:
            tier = "CRITICAL"
            action = "FREEZE_AND_FLAG"
        elif composite >= 0.50:
            tier = "HIGH"
            action = "MANUAL_INVESTIGATION"
        elif composite >= 0.25:
            tier = "MEDIUM"
            action = "ENHANCED_MONITORING"
        else:
            tier = "LOW"
            action = "AUTO_PASS"

        return {
            "composite_risk_score": round(composite, 4),
            "risk_tier": tier,
            "recommended_action": action,
            "component_breakdown": {
                "xgboost_risk": round(float(xgb_score), 4),
                "gnn_topological_risk": round(float(gnn_score), 4),
                "anomaly_reconstruction_risk": round(float(anomaly_score), 4),
                "heuristics_risk": round(float(heuristic_score), 4)
            }
        }
