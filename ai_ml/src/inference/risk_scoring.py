"""
Risk Scoring Module

Converts ML model outputs into normalized 0-100 risk scores with:
- Configurable thresholds
- Investigation priority levels
- Explainability signals
- Human-in-the-loop design

Risk score indicates INVESTIGATION PRIORITY, not criminality or guilt.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Standardized risk level categories."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskThresholds:
    """Configurable risk score thresholds."""
    
    low_max: float = 20
    moderate_max: float = 40
    elevated_max: float = 60
    high_max: float = 80
    critical_min: float = 81
    
    def get_level(self, score: float) -> RiskLevel:
        """Map risk score to risk level."""
        if score <= self.low_max:
            return RiskLevel.LOW
        elif score <= self.moderate_max:
            return RiskLevel.MODERATE
        elif score <= self.elevated_max:
            return RiskLevel.ELEVATED
        elif score <= self.high_max:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


class RiskScorer:
    """Converts model outputs to normalized risk scores."""
    
    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        """
        Initialize risk scorer.
        
        Args:
            thresholds: Custom risk thresholds. Defaults to standard thresholds.
        """
        self.thresholds = thresholds or RiskThresholds()
    
    def score_from_anomaly(
        self,
        anomaly_score: float,
        scale_min: float = 0.0,
        scale_max: float = 1.0
    ) -> int:
        """
        Convert anomaly score (typically 0-1) to risk score (0-100).
        
        Args:
            anomaly_score: Raw anomaly score from model (e.g., Isolation Forest)
            scale_min: Minimum possible value of input anomaly score
            scale_max: Maximum possible value of input anomaly score
        
        Returns:
            Risk score (0-100)
        """
        # Normalize anomaly score to [0, 1]
        if scale_max == scale_min:
            normalized = 0.5
        else:
            normalized = (anomaly_score - scale_min) / (scale_max - scale_min)
        
        # Clip to valid range
        normalized = np.clip(normalized, 0.0, 1.0)
        
        # Scale to 0-100
        risk_score = int(normalized * 100)
        
        logger.debug(f"Anomaly {anomaly_score:.3f} -> Risk {risk_score}/100")
        return risk_score
    
    def score_from_probability(
        self,
        probability: float,
        method: str = "linear"
    ) -> int:
        """
        Convert classification probability to risk score.
        
        Args:
            probability: Probability of illicit class (0-1)
            method: Scaling method ('linear', 'sqrt', 'log')
        
        Returns:
            Risk score (0-100)
        """
        probability = np.clip(probability, 0.0, 1.0)
        
        if method == "linear":
            risk_score = int(probability * 100)
        elif method == "sqrt":
            # Square root scaling (emphasizes lower probabilities)
            risk_score = int(np.sqrt(probability) * 100)
        elif method == "log":
            # Log scaling (emphasizes higher probabilities)
            # log(1 + x) to avoid log(0)
            risk_score = int(np.log1p(probability) / np.log1p(1.0) * 100)
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        logger.debug(f"Probability {probability:.3f} -> Risk {risk_score}/100")
        return risk_score
    
    def score_from_ensemble(
        self,
        scores: List[Tuple[float, float]],
        weights: Optional[List[float]] = None
    ) -> int:
        """
        Combine multiple model scores using weighted average.
        
        Args:
            scores: List of (score, weight) tuples or just scores if weights provided separately
            weights: Optional weights for each score. Defaults to equal weights.
        
        Returns:
            Ensemble risk score (0-100)
        """
        if weights is None:
            weights = [1.0] * len(scores)
        
        if len(scores) != len(weights):
            raise ValueError("Number of scores must match number of weights")
        
        # Normalize weights
        weight_sum = sum(weights)
        normalized_weights = [w / weight_sum for w in weights]
        
        # Weighted average
        ensemble_score = sum(s * w for s, w in zip(scores, normalized_weights))
        ensemble_score = int(np.clip(ensemble_score, 0, 100))
        
        logger.debug(f"Ensemble scores {scores} -> Risk {ensemble_score}/100")
        return ensemble_score
    
    def get_risk_level(self, risk_score: int) -> RiskLevel:
        """Get risk level for a given score."""
        return self.thresholds.get_level(risk_score)


@dataclass
class RiskScoreResult:
    """Result of risk scoring for a transaction/entity."""
    
    entity_id: str
    risk_score: int
    risk_level: RiskLevel
    anomaly_score: Optional[float] = None
    classification_probability: Optional[float] = None
    model_version: str = "v1.0"
    top_features: List[str] = None
    investigation_signals: List[str] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "entity_id": self.entity_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "anomaly_score": self.anomaly_score,
            "classification_probability": self.classification_probability,
            "model_version": self.model_version,
            "top_features": self.top_features or [],
            "investigation_signals": self.investigation_signals or [],
            "confidence": self.confidence,
            "disclaimer": (
                "Risk score indicates investigation priority and does not establish "
                "criminality or identify a person. Final determination by human investigator."
            )
        }
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"[{self.risk_level.value}] "
            f"Entity: {self.entity_id} | "
            f"Score: {self.risk_score}/100 | "
            f"Signals: {', '.join(self.investigation_signals or ['None'])}  "
        )


class InvestigationSignalGenerator:
    """Generates human-readable investigation signals from model outputs."""
    
    @staticmethod
    def generate_signals_from_features(
        top_features: List[Tuple[str, float]],
        risk_score: int
    ) -> List[str]:
        """
        Generate investigation signals based on top contributing features.
        
        Args:
            top_features: List of (feature_name, importance) tuples
            risk_score: Computed risk score
        
        Returns:
            List of human-readable investigation signals
        """
        signals = []
        
        if risk_score >= 80:
            signals.append("Extremely anomalous transaction behavior")
        elif risk_score >= 60:
            signals.append("Highly anomalous transaction pattern")
        elif risk_score >= 40:
            signals.append("Moderately anomalous activity detected")
        
        # Feature-specific signals
        feature_signal_map = {
            "transaction_velocity": "High transaction velocity",
            "fund_dispersion": "Fund dispersion pattern detected",
            "rapid_mixing": "Rapid fund mixing behavior",
            "counterparty_count": "Unusual number of counterparties",
            "transaction_burst": "Transaction burst detected",
            "fund_consolidation": "Fund consolidation pattern",
            "temporal_anomaly": "Unusual temporal behavior",
            "graph_centrality": "High centrality in transaction network",
            "amount_variance": "Unusual transaction amount variance",
            "connection_frequency": "Unusual connection frequency"
        }
        
        for feature_name, importance in top_features[:3]:  # Top 3 features
            for key, signal in feature_signal_map.items():
                if key.lower() in feature_name.lower():
                    signals.append(signal)
                    break
        
        if not signals:
            signals = ["Potential anomalies detected - review recommended"]
        
        return signals[:5]  # Limit to top 5 signals
    
    @staticmethod
    def generate_signals_from_graph_properties(
        graph_properties: Dict[str, Any]
    ) -> List[str]:
        """
        Generate signals based on graph structural properties.
        
        Args:
            graph_properties: Dictionary of graph-level properties
        
        Returns:
            List of investigation signals
        """
        signals = []
        
        if graph_properties.get("in_degree", 0) > 100:
            signals.append("High in-degree (receives from many sources)")
        
        if graph_properties.get("out_degree", 0) > 100:
            signals.append("High out-degree (sends to many destinations)")
        
        if graph_properties.get("clustering_coefficient", 0) < 0.1:
            signals.append("Low clustering coefficient (fragmented connections)")
        
        if graph_properties.get("pagerank", 0) > 0.001:
            signals.append("High network importance (PageRank)")
        
        if graph_properties.get("connected_component_size", 0) > 1000:
            signals.append("Part of large connected transaction component")
        
        return signals


class InvestigationPrioritizer:
    """Ranks and prioritizes investigation leads."""
    
    def __init__(self, max_results: int = 100):
        """
        Initialize prioritizer.
        
        Args:
            max_results: Maximum number of top results to return
        """
        self.max_results = max_results
    
    def prioritize(
        self,
        results: List[RiskScoreResult]
    ) -> List[RiskScoreResult]:
        """
        Sort results by risk score (descending) and return top N.
        
        Args:
            results: List of risk score results
        
        Returns:
            Top N results sorted by risk score
        """
        sorted_results = sorted(results, key=lambda x: x.risk_score, reverse=True)
        return sorted_results[:self.max_results]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    scorer = RiskScorer()
    
    # Example 1: Score from anomaly
    anomaly_score = 0.75
    risk = scorer.score_from_anomaly(anomaly_score, scale_min=0.0, scale_max=1.0)
    print(f"Anomaly {anomaly_score:.2f} -> Risk {risk}/100 ({scorer.get_risk_level(risk).value})")
    
    # Example 2: Score from probability
    prob = 0.85
    risk = scorer.score_from_probability(prob)
    print(f"Probability {prob:.2f} -> Risk {risk}/100 ({scorer.get_risk_level(risk).value})")
    
    # Example 3: Ensemble score
    scores = [75, 82, 70]
    risk = scorer.score_from_ensemble(scores, weights=[0.4, 0.4, 0.2])
    print(f"Ensemble {scores} -> Risk {risk}/100 ({scorer.get_risk_level(risk).value})")
    
    # Example 4: Full result
    result = RiskScoreResult(
        entity_id="TX123456",
        risk_score=82,
        risk_level=RiskLevel.HIGH,
        anomaly_score=0.78,
        model_version="ensemble_v1.0",
        top_features=[("fund_dispersion", 0.34), ("transaction_velocity", 0.28)],
        investigation_signals=[
            "High transaction velocity",
            "Fund dispersion pattern detected",
            "High network centrality"
        ]
    )
    print(f"\nRisk Result:\n{result}")
    print(f"\nAPI Response:\n{result.to_dict()}")
