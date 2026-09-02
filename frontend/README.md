# 🖥️ Frontend & Forensic Dashboard Layer (`frontend/` & `dashboard/`)

This directory contains the user interface and interactive investigative tools:

- **Entrypoint**:
  - `frontend/app.py` or `dashboard/app.py`: Main Streamlit web application.
- **Investigative Forensic Pages**:
  - `01_Overview.py`: Key performance metrics, transaction volumes, and archetype distributions.
  - `02_Alert_Ranking.py`: Triage queue with interactive dossier cards and risk level badges.
  - `03_Transaction_Explorer.py`: Deep-dive inspection of input/output script types, amounts, and fees.
  - `04_Wallet_Forensics.py`: Longitudinal wallet interaction history and colocation metrics.
  - `05_Network_Graph.py`: Interactive 2D PyVis sub-graph and ego-network explorer.
  - `06_Geo_Analysis.py`: Geographic heatmaps and hosting ASN distribution.
  - `07_SHAP_Explainability.py`: Interactive SHAP decision waterfall and feature importance breakdown.
  - `08_Model_Benchmarks.py`: Multi-model PR-AUC, ROC-AUC, and precision-recall curves.
  - `behavioral_clustering.py`: 2D PCA cluster projection of discovered mixing rings.
  - `duckdb_analytics.py`: In-memory SQL console and custom query explorer.
