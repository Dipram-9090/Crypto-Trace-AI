# 🤖 Machine Learning & AI Modeling Pipeline

CryptoTrace AI employs a hybrid ensemble combining supervised gradient boosting, unsupervised anomaly detection, inductive Graph Neural Networks, and behavioral clustering.

---

## 1. Model Architecture Overview

| Model Component | Framework | Target / Task | Metric Evaluated |
| :--- | :--- | :--- | :--- |
| **XGBoost Classifier** | `xgboost` | Supervised illicit transaction classification | PR-AUC, Recall@100, F1 |
| **Isolation Forest** | `scikit-learn` | Unsupervised structural anomaly detection | Out-of-distribution score |
| **GraphSAGE GNN** | `PyTorch` | Inductive neighborhood representation learning | Node classification accuracy |
| **DBSCAN + PCA** | `scikit-learn` | Latent behavioral clustering & archetype discovery | Cluster silhouette & variance |
| **Ransomware Classifier** | `xgboost` | BitcoinHeist address graph ransomware detection | PR-AUC, ROC-AUC |

---

## 2. Anti-Data Leakage Temporal Splitting

To prevent lookahead bias in time-series blockchain data, all models are evaluated on strictly forward-looking chronological partitions:
- **Training Set (70%)**: Earliest time steps ($t \in [0, 0.70 N]$).
- **Validation Set (15%)**: Intermediate time steps ($t \in [0.70 N, 0.85 N]$).
- **Test Set (15%)**: Held-out future time steps ($t \in [0.85 N, N]$).
