"""
Model Evaluation Metrics Module

Computes comprehensive evaluation metrics including:
- Classification metrics (Precision, Recall, F1, ROC-AUC, PR-AUC)
- Confusion matrix
- Class distribution analysis
- Imbalance handling metrics
"""

import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)

logger = logging.getLogger(__name__)


class ClassificationMetrics:
    """Computes and stores classification metrics."""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray, 
                 y_pred_proba: Optional[np.ndarray] = None):
        """
        Initialize metrics calculator.
        
        Args:
            y_true: True binary labels (0 or 1)
            y_pred: Predicted binary labels (0 or 1)
            y_pred_proba: Predicted probabilities for positive class (0-1)
        """
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_pred_proba = y_pred_proba
        self.metrics = {}
        
        self._compute_all_metrics()
    
    def _compute_all_metrics(self):
        """Compute all available metrics."""
        
        # Basic classification metrics
        self.metrics["precision"] = precision_score(self.y_true, self.y_pred, zero_division=0)
        self.metrics["recall"] = recall_score(self.y_true, self.y_pred, zero_division=0)
        self.metrics["f1"] = f1_score(self.y_true, self.y_pred, zero_division=0)
        
        # Probability-based metrics
        if self.y_pred_proba is not None:
            try:
                self.metrics["roc_auc"] = roc_auc_score(self.y_true, self.y_pred_proba)
            except Exception as e:
                logger.warning(f"Could not compute ROC-AUC: {str(e)}")
                self.metrics["roc_auc"] = None
            
            try:
                self.metrics["pr_auc"] = average_precision_score(self.y_true, self.y_pred_proba)
            except Exception as e:
                logger.warning(f"Could not compute PR-AUC: {str(e)}")
                self.metrics["pr_auc"] = None
        
        # Confusion matrix
        cm = confusion_matrix(self.y_true, self.y_pred)
        self.metrics["confusion_matrix"] = cm
        
        # TN, FP, FN, TP
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            self.metrics["true_negatives"] = tn
            self.metrics["false_positives"] = fp
            self.metrics["false_negatives"] = fn
            self.metrics["true_positives"] = tp
            
            # Specificity
            if tn + fp > 0:
                self.metrics["specificity"] = tn / (tn + fp)
            
            # Sensitivity (same as recall)
            if tp + fn > 0:
                self.metrics["sensitivity"] = tp / (tp + fn)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        result = {}
        for k, v in self.metrics.items():
            if isinstance(v, np.ndarray):
                result[k] = v.tolist()
            else:
                result[k] = v
        return result
    
    def print_report(self):
        """Print formatted metrics report."""
        print("\n" + "=" * 70)
        print("CLASSIFICATION METRICS REPORT")
        print("=" * 70 + "\n")
        
        # Basic metrics
        print("Classification Scores:")
        print(f"  Precision: {self.metrics['precision']:.4f}")
        print(f"  Recall:    {self.metrics['recall']:.4f}")
        print(f"  F1 Score:  {self.metrics['f1']:.4f}")
        
        # Probability metrics
        if self.metrics.get("roc_auc"):
            print(f"  ROC-AUC:   {self.metrics['roc_auc']:.4f}")
        if self.metrics.get("pr_auc"):
            print(f"  PR-AUC:    {self.metrics['pr_auc']:.4f}")
        
        # Confusion Matrix
        cm = self.metrics["confusion_matrix"]
        if cm.shape == (2, 2):
            print(f"\nConfusion Matrix:")
            print(f"  TN={cm[0,0]}, FP={cm[0,1]}")
            print(f"  FN={cm[1,0]}, TP={cm[1,1]}")
            
            if "specificity" in self.metrics:
                print(f"\nAdditional Metrics:")
                print(f"  Specificity: {self.metrics['specificity']:.4f}")
                print(f"  Sensitivity: {self.metrics['sensitivity']:.4f}")
        
        print("\n" + "=" * 70)


class AnomalyDetectionMetrics:
    """Computes metrics for anomaly detection models."""
    
    def __init__(self, y_true: np.ndarray, anomaly_scores: np.ndarray,
                 threshold: float = 0.5):
        """
        Initialize anomaly detection metrics.
        
        Args:
            y_true: True binary labels (0=normal, 1=anomaly)
            anomaly_scores: Anomaly scores (typically 0-1)
            threshold: Classification threshold
        """
        self.y_true = y_true
        self.anomaly_scores = anomaly_scores
        self.threshold = threshold
        
        # Convert scores to predictions using threshold
        self.y_pred = (anomaly_scores >= threshold).astype(int)
        
        self.metrics = {}
        self._compute_metrics()
    
    def _compute_metrics(self):
        """Compute anomaly detection metrics."""
        
        # Use classification metrics
        self.metrics["precision"] = precision_score(self.y_true, self.y_pred, zero_division=0)
        self.metrics["recall"] = recall_score(self.y_true, self.y_pred, zero_division=0)
        self.metrics["f1"] = f1_score(self.y_true, self.y_pred, zero_division=0)
        
        # ROC-AUC
        try:
            self.metrics["roc_auc"] = roc_auc_score(self.y_true, self.anomaly_scores)
        except:
            self.metrics["roc_auc"] = None
        
        # Anomaly detection specific
        anomaly_indices = self.y_pred == 1
        normal_indices = self.y_pred == 0
        
        if len(self.anomaly_scores[anomaly_indices]) > 0:
            self.metrics["mean_anomaly_score"] = np.mean(self.anomaly_scores[anomaly_indices])
        
        if len(self.anomaly_scores[normal_indices]) > 0:
            self.metrics["mean_normal_score"] = np.mean(self.anomaly_scores[normal_indices])
        
        # Anomalies detected
        self.metrics["anomalies_detected"] = np.sum(self.y_pred == 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.metrics


class ImbalanceMetrics:
    """Metrics specifically for handling class imbalance."""
    
    def __init__(self, y_true: np.ndarray):
        """
        Initialize imbalance metrics.
        
        Args:
            y_true: True labels
        """
        self.y_true = y_true
        self.metrics = {}
        self._compute_imbalance_metrics()
    
    def _compute_imbalance_metrics(self):
        """Compute class imbalance metrics."""
        
        unique, counts = np.unique(self.y_true, return_counts=True)
        
        # Class distribution
        self.metrics["class_distribution"] = dict(zip(unique, counts))
        
        # Imbalance ratio
        if len(counts) == 2:
            majority_count = max(counts)
            minority_count = min(counts)
            self.metrics["imbalance_ratio"] = majority_count / minority_count
        
        # Minority class percentage
        total_samples = len(self.y_true)
        for class_label, count in zip(unique, counts):
            percentage = (count / total_samples) * 100
            self.metrics[f"class_{class_label}_percentage"] = percentage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.metrics
    
    def print_report(self):
        """Print imbalance report."""
        print("\n" + "=" * 70)
        print("CLASS IMBALANCE REPORT")
        print("=" * 70 + "\n")
        
        dist = self.metrics.get("class_distribution", {})
        total = sum(dist.values())
        
        for class_label, count in sorted(dist.items()):
            percentage = (count / total) * 100
            bar_length = int(percentage / 2)
            bar = "█" * bar_length
            print(f"Class {class_label}: {count:6d} ({percentage:5.2f}%) {bar}")
        
        if "imbalance_ratio" in self.metrics:
            print(f"\nImbalance Ratio: {self.metrics['imbalance_ratio']:.2f}:1")
        
        print("\n" + "=" * 70)


class ModelEvaluator:
    """Comprehensive model evaluator."""
    
    def __init__(self, y_true: np.ndarray):
        """
        Initialize evaluator.
        
        Args:
            y_true: True labels
        """
        self.y_true = y_true
    
    def evaluate_classifier(self, y_pred: np.ndarray,
                           y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Evaluate classification model.
        
        Args:
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
        
        Returns:
            Dictionary of metrics
        """
        metrics = ClassificationMetrics(self.y_true, y_pred, y_pred_proba)
        return metrics.to_dict()
    
    def evaluate_anomaly_detector(self, anomaly_scores: np.ndarray,
                                 threshold: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate anomaly detection model.
        
        Args:
            anomaly_scores: Anomaly scores
            threshold: Classification threshold
        
        Returns:
            Dictionary of metrics
        """
        metrics = AnomalyDetectionMetrics(self.y_true, anomaly_scores, threshold)
        return metrics.to_dict()
    
    def get_imbalance_metrics(self) -> Dict[str, Any]:
        """Get class imbalance metrics."""
        metrics = ImbalanceMetrics(self.y_true)
        return metrics.to_dict()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 0, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.9, 0.4, 0.3, 0.8, 0.7, 0.2, 0.95, 0.85])
    
    # Classification metrics
    metrics = ClassificationMetrics(y_true, y_pred, y_proba)
    metrics.print_report()
    
    # Imbalance metrics
    imbalance = ImbalanceMetrics(y_true)
    imbalance.print_report()
