"""
Multi-modal Risk Scoring Engine.
"""
import numpy as np
import pandas as pd
from typing import Optional
from src.cryptotrace.utils.io import load_yaml


class RiskEngine:
    """Combines Supervised ML, Anomaly Detection, Graph Topology, and Behavioral Evidence."""
    def __init__(
        self,
        w_ml: float = 0.50,
        w_anomaly: float = 0.20,
        w_graph: float = 0.20,
        w_behavioral: float = 0.10,
        threshold_low: float = 30.0,
        threshold_medium: float = 60.0,
        threshold_high: float = 80.0
    ):
        self.w_ml = w_ml
        self.w_anomaly = w_anomaly
        self.w_graph = w_graph
        self.w_behavioral = w_behavioral
        self.threshold_low = threshold_low
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high

    @classmethod
    def from_config(cls, config_path: str = "configs/config.yaml") -> "RiskEngine":
        cfg = load_yaml(config_path)
        weights = cfg.get("risk_scoring", {}).get("weights", {})
        return cls(
            w_ml=weights.get("ml_score", 0.50),
            w_anomaly=weights.get("anomaly_score", 0.20),
            w_graph=weights.get("graph_score", 0.20),
            w_behavioral=weights.get("behavioral_score", 0.10)
        )

    def classify_risk_tier(self, score: float) -> str:
        if score >= self.threshold_high: return "CRITICAL"
        elif score >= self.threshold_medium: return "HIGH"
        elif score >= self.threshold_low: return "MEDIUM"
        else: return "LOW"

    def compute_behavioral_score(self, row: pd.Series) -> float:
        burst = float(row.get("burst_score", 0.0)) * 35.0
        fanout = min(1.0, float(row.get("fan_out_ratio", 1.0)) / 10.0) * 30.0
        shared_ip = float(row.get("shared_infrastructure_indicator", 0.0)) * 35.0
        return float(np.clip(burst + fanout + shared_ip, 0.0, 100.0))

    def compute_composite_risk(
        self,
        ml_prob: float,
        anomaly_score: float,
        graph_score: float,
        row_series: Optional[pd.Series] = None,
        behavioral_score: Optional[float] = None
    ) -> tuple[float, str]:
        ml_scaled = np.clip(ml_prob * 100.0, 0.0, 100.0)
        anom_scaled = np.clip(anomaly_score, 0.0, 100.0)
        graph_scaled = np.clip(graph_score, 0.0, 100.0)

        if behavioral_score is None and row_series is not None:
            behav_scaled = self.compute_behavioral_score(row_series)
        elif behavioral_score is not None:
            behav_scaled = np.clip(behavioral_score, 0.0, 100.0)
        else:
            behav_scaled = 0.0

        final_score = (
            self.w_ml * ml_scaled +
            self.w_anomaly * anom_scaled +
            self.w_graph * graph_scaled +
            self.w_behavioral * behav_scaled
        )
        final_score = float(np.clip(round(final_score, 1), 0.0, 100.0))
        tier = self.classify_risk_tier(final_score)
        return final_score, tier
