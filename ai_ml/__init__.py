"""
CryptoTrace AI - Artificial Intelligence & Machine Learning Domain Module.
Covers Supervised Classification (XGBoost, Ransomware), Anomaly Detection (Isolation Forest),
Inductive Graph Neural Networks (GraphSAGE, GCN, GAT), Behavioral Clustering (DBSCAN + PCA),
and Explainable AI (SHAP & Graph Neighborhood Attribution).
"""

from src.cryptotrace.models.classical.xgboost_model import CryptoXGBoostClassifier
from src.cryptotrace.models.classical.random_forest import RandomForestBaseline
from src.cryptotrace.models.classical.baseline import LogisticRegressionBaseline
from src.cryptotrace.models.anomaly.isolation_forest import CryptoIsolationForest
from src.cryptotrace.models.clustering.hdbscan_model import BehavioralClusterer
from src.cryptotrace.models.ransomware_model import RansomwareClassifier
from src.cryptotrace.models.graph_ml.graphsage import CryptoGraphSAGE
from src.cryptotrace.models.graph_ml.gcn import GCNNet
from src.cryptotrace.models.graph_ml.gat import GATNet
from src.cryptotrace.explainability.shap import CryptoSHAPExplainer
from src.cryptotrace.explainability.graph_explainer import GraphNeighborhoodExplainer

__all__ = [
    "CryptoXGBoostClassifier",
    "RandomForestBaseline",
    "LogisticRegressionBaseline",
    "CryptoIsolationForest",
    "BehavioralClusterer",
    "RansomwareClassifier",
    "CryptoGraphSAGE",
    "GCNNet",
    "GATNet",
    "CryptoSHAPExplainer",
    "GraphNeighborhoodExplainer",
]
