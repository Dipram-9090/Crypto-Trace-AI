"""Real-Time & Batch AI Inference Engine for Crypto-Trace-AI."""

import logging
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

from ai_ml.models import FraudXGBoostClassifier, GraphSAGETxClassifier, TransactionAutoencoder, ForensicEnsembleScorer
from ai_ml.anomaly_detection import IsolationForestDetector
from ai_ml.explainability import ForensicSHAPExplainer, ForensicReportGenerator

logger = logging.getLogger("cryptotrace.ai_ml.inference")


class ForensicInferenceEngine:
    """Production inference engine orchestrating all models, risk scoring, explainability, and SAR generation."""

    def __init__(self):
        self.xgb_model = FraudXGBoostClassifier()
        self.iforest_model = IsolationForestDetector()
        self.ensemble = ForensicEnsembleScorer()
        self.explainer = ForensicSHAPExplainer(model=getattr(self.xgb_model, "model", None))

    def evaluate_transaction(self, tx_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an incoming blockchain transaction payload and returns a comprehensive forensic verdict."""
        amount = float(tx_dict.get("amount", 1.0))
        sender = tx_dict.get("sender", "0x0000")
        receiver = tx_dict.get("receiver", "0x0000")
        chain = tx_dict.get("chain", "ethereum")

        # Heuristic features
        velocity = float(tx_dict.get("tx_velocity_1h", 1.0))
        time_diff = float(tx_dict.get("time_diff_secs", 3600.0))
        fan_ratio = float(tx_dict.get("fan_ratio", 1.0))
        pagerank = float(tx_dict.get("pagerank", 0.001))

        # Synthetic feature vector for models
        feature_vector = pd.DataFrame([{
            "amount": amount,
            "velocity": velocity,
            "time_diff": time_diff,
            "fan_ratio": fan_ratio,
            "pagerank": pagerank,
            "log_amount": np.log1p(amount)
        }])

        # 1. Supervised XGBoost score
        xgb_risk = float(self.xgb_model.predict_risk_score(feature_vector)[0])

        # 2. Isolation Forest score
        anomaly_risk = float(self.iforest_model.score_samples(feature_vector)[0])

        # 3. GNN Graph topological score (proxy)
        gnn_risk = float(np.clip(0.3 * (1.0 - np.exp(-10 * pagerank)) + 0.7 * (velocity > 5), 0.05, 0.95))

        # 4. Heuristic risk
        heuristic_risk = 0.0
        if amount > 50.0 and velocity > 8:
            heuristic_risk += 0.4
        if "mixer" in sender.lower() or "tornadocash" in sender.lower():
            heuristic_risk += 0.8
        heuristic_risk = min(1.0, heuristic_risk)

        # 5. Composite Risk
        composite = self.ensemble.compute_composite_risk(
            xgb_score=xgb_risk,
            gnn_score=gnn_risk,
            anomaly_score=anomaly_risk,
            heuristic_score=heuristic_risk
        )

        # 6. Explainability
        shap_res = self.explainer.explain_instance(feature_vector)
        narrative = ForensicReportGenerator.generate_narrative(tx_dict, composite, shap_res["top_features"])

        return {
            "transaction_hash": tx_dict.get("tx_hash", "0x" + "a" * 64),
            "chain": chain,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "risk_verdict": composite,
            "explainability": shap_res,
            "narrative_report": narrative
        }
