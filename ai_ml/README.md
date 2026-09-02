# 🤖 Artificial Intelligence & Machine Learning Layer (`ai_ml/`)

This directory contains all predictive, graph neural network, unsupervised anomaly detection, and explainability models:

- **Supervised Classifiers**:
  - `xgboost_model.py`: Gradient-boosted decision trees for primary illicit transaction classification (**PR-AUC: 0.9985, Recall@100: 77.5%**).
  - `ransomware_model.py`: Specialized XGBoost model trained on BitcoinHeist topological address graph metrics.
  - `random_forest.py` & `baseline.py`: Benchmark models for rigorous ablation studies.
- **Unsupervised Anomaly Detection**:
  - `isolation_forest.py`: Tree-based isolation anomaly detection for novel money laundering archetypes.
  - `clustering/`: DBSCAN & PCA unsupervised dimensionality reduction discovering latent mixing rings and peeling chains.
- **Inductive Graph Neural Networks (GNN)**:
  - `graphsage.py`: 2-hop neighborhood aggregator learning relational node representations.
  - `gcn.py` & `gat.py`: Graph Convolutional and Multi-head Graph Attention networks.
- **Explainable AI (XAI)**:
  - `shap_explainer.py`: Exact game-theoretic Shapley value attribution providing human-readable justifications and machine-readable JSON dossiers.
  - `graph_explainer.py`: $k$-hop influential sub-graph extraction for investigator verification.
