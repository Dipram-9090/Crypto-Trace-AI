# 🔬 Machine Learning Pipeline & Model Cards

## 1. Training & Temporal Splitting Methodology

To simulate realistic forward-looking forensic detection, CryptoTrace AI applies **chronological temporal splitting** rather than random K-Fold cross validation:

- **Train Set (First 70%)**: Historical baseline transactions.
- **Validation Set (Next 15%)**: Hyperparameter tuning and early stopping.
- **Test Set (Final 15%)**: Unseen future transactions.

---

## 2. Models Architecture

### Model A: XGBoost Classifier (Primary Supervised)
- **Objective**: Binary classification on engineered tabular feature vectors.
- **Handling Imbalance**: Scaled positive class weights (`scale_pos_weight: 10.0`).
- **Explainability**: Coupled with SHAP TreeExplainer to compute exact feature attributions.

### Model B: Isolation Forest (Unsupervised Behavioral Anomaly)
- **Objective**: Detect novel or unlabelled structural deviations and peeling chains.
- **Normalization**: Translates raw isolation path length into a 0–100 intuitive anomaly score.

### Model C: GraphSAGE (Graph Neural Network)
- **Objective**: 2-layer inductive message passing over heterogeneous node graphs.
- **Aggregation**: Normalized mean aggregator capturing structural neighborhood risk propagation.
