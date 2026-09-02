"""
Confidence Interval & Calibration Engine for Investigative Lead Scoring.
"""

import numpy as np


class ConfidenceScorer:
    """Calculates evidence convergence and confidence score across multiple models."""

    @staticmethod
    def compute_confidence(ml_prob: float, anomaly_score: float, graph_score: float) -> float:
        """Calculates multi-modal consensus confidence between 0.0 and 1.0."""
        # Scale all to [0, 1]
        m = ml_prob
        a = np.clip(anomaly_score / 100.0, 0.0, 1.0)
        g = np.clip(graph_score / 100.0, 0.0, 1.0)

        signals = [m, a, g]
        high_signals = sum(1 for s in signals if s >= 0.5)

        if high_signals == 3:
            return 0.95  # Triple consensus
        elif high_signals == 2:
            return 0.80  # Dual consensus
        elif high_signals == 1:
            return 0.60  # Single signal
        else:
            return 0.30  # Low confidence
