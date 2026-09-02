"""
Explainable Blockchain Risk Scoring Engine.
Combines transparent rule-based forensic heuristics with unsupervised ML anomaly detection (IsolationForest).
Produces normalized 0-100 risk scores categorized into LOW, MEDIUM, HIGH, and CRITICAL tiers with explainable signal breakdowns.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from src.cryptotrace.blockchain.models import BitcoinTransaction, RiskEvaluation, ForensicSignal
from src.cryptotrace.blockchain.heuristics.engine import ForensicHeuristicsEngine
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BlockchainRiskEngine:
    """Transparent, explainable risk scoring engine for Bitcoin transaction forensics."""

    def __init__(
        self,
        weight_heuristic: float = 0.60,
        weight_ml_anomaly: float = 0.25,
        weight_graph: float = 0.15,
        threshold_low: float = 30.0,
        threshold_medium: float = 60.0,
        threshold_high: float = 80.0,
    ):
        self.w_heuristic = weight_heuristic
        self.w_ml = weight_ml_anomaly
        self.w_graph = weight_graph
        self.threshold_low = threshold_low
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high
        self.heuristics_engine = ForensicHeuristicsEngine()
        self.iso_forest: Optional[IsolationForest] = None
        self._is_ml_fitted = False

    def classify_tier(self, score: float) -> str:
        """Classify numerical risk score (0-100) into standardized risk level tier."""
        if score >= self.threshold_high:
            return "CRITICAL"
        elif score >= self.threshold_medium:
            return "HIGH"
        elif score >= self.threshold_low:
            return "MEDIUM"
        else:
            return "LOW"

    def fit_ml_anomaly_detector(self, feature_matrix: np.ndarray):
        """Fit an IsolationForest anomaly detector on transaction features."""
        if len(feature_matrix) < 5:
            return
        self.iso_forest = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42,
        )
        self.iso_forest.fit(feature_matrix)
        self._is_ml_fitted = True

    def compute_heuristic_score(self, signals: List[ForensicSignal]) -> float:
        """Sum and normalize heuristic signal scores."""
        raw_sum = sum(s.score for s in signals)
        return float(np.clip(raw_sum, 0.0, 100.0))

    def evaluate_transaction(
        self,
        tx: BitcoinTransaction,
        graph_centrality: float = 0.0,
        feature_vector: Optional[np.ndarray] = None,
        all_transactions: Optional[Dict[str, BitcoinTransaction]] = None,
    ) -> RiskEvaluation:
        """
        Evaluate a single Bitcoin transaction, producing an explainable RiskEvaluation.
        """
        # 1. Run rule-based heuristic detectors
        signals = self.heuristics_engine.analyze_transaction(tx, all_transactions)
        heuristic_score = self.compute_heuristic_score(signals)

        # 2. Compute ML anomaly score if detector is fitted and vector is given
        ml_score = 0.0
        if self._is_ml_fitted and self.iso_forest is not None and feature_vector is not None:
            try:
                # Decision function returns negative for anomalies, positive for inliers
                decision = self.iso_forest.decision_function(feature_vector.reshape(1, -1))[0]
                # Map decision [-0.5, 0.5] to [100, 0]
                ml_score = float(np.clip((0.5 - decision) * 100.0, 0.0, 100.0))
            except Exception:
                ml_score = 0.0

        # 3. Graph topology score
        graph_score = float(np.clip(graph_centrality * 100.0, 0.0, 100.0))

        # 4. Composite weighted risk calculation
        # If ML detector is not fitted, dynamically adjust heuristic weighting
        effective_w_heuristic = self.w_heuristic if self._is_ml_fitted else (self.w_heuristic + self.w_ml)
        composite = (
            effective_w_heuristic * heuristic_score
            + (self.w_ml * ml_score if self._is_ml_fitted else 0.0)
            + self.w_graph * graph_score
        )
        if signals:
            max_sig = max(s.score for s in signals)
            composite = max(composite, max_sig * 0.90)

        final_score = float(np.clip(round(composite, 1), 0.0, 100.0))
        tier = self.classify_tier(final_score)

        return RiskEvaluation(
            entity_id=tx.txid,
            entity_type="transaction",
            risk_score=final_score,
            risk_level=tier,
            heuristic_score=heuristic_score,
            ml_anomaly_score=ml_score,
            graph_score=graph_score,
            behavioral_score=heuristic_score,
            signals=signals,
        )

    def evaluate_address(
        self,
        address: str,
        transaction_evaluations: List[RiskEvaluation],
        fan_in: int,
        fan_out: int,
        pagerank: float = 0.0,
    ) -> RiskEvaluation:
        """
        Aggregate transaction-level risk evaluations and topology into an address-level RiskEvaluation.
        """
        signals: List[ForensicSignal] = []

        if not transaction_evaluations:
            return RiskEvaluation(
                entity_id=address,
                entity_type="address",
                risk_score=0.0,
                risk_level="LOW",
                heuristic_score=0.0,
                signals=[],
            )

        tx_scores = [te.risk_score for te in transaction_evaluations]
        max_tx_score = max(tx_scores)
        mean_tx_score = float(np.mean(tx_scores))

        # Collect unique signals from connected transactions
        seen_types = set()
        for te in transaction_evaluations:
            for s in te.signals:
                if s.type not in seen_types:
                    seen_types.add(s.type)
                    signals.append(s)

        # Address topology signals
        if fan_out >= 15:
            signals.append(
                ForensicSignal(
                    type="DISPERSION_HUB",
                    severity="high",
                    score=25.0,
                    explanation=f"Address acts as high-dispersion hub with {fan_out} outgoing counterparties.",
                )
            )
        if fan_in >= 15:
            signals.append(
                ForensicSignal(
                    type="COLLECTION_HUB",
                    severity="high",
                    score=25.0,
                    explanation=f"Address acts as large collection hub with {fan_in} incoming funding sources.",
                )
            )

        # Weighted address score: 50% max tx, 30% mean tx, 20% pagerank
        address_score = (0.50 * max_tx_score) + (0.30 * mean_tx_score) + (0.20 * min(100.0, pagerank * 1000.0))
        final_score = float(np.clip(round(address_score, 1), 0.0, 100.0))
        tier = self.classify_tier(final_score)

        return RiskEvaluation(
            entity_id=address,
            entity_type="address",
            risk_score=final_score,
            risk_level=tier,
            heuristic_score=round(mean_tx_score, 1),
            graph_score=round(pagerank * 100.0, 1),
            signals=signals,
        )
