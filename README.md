# 🛡️ CryptoTrace AI: Multi-Modal Graph & Machine Learning Forensic Analytics

> **Offline-capable, Explainable Forensic AI for Suspicious Bitcoin Transaction Detection, Network Infrastructure Correlation, and Ranked Lead Generation.**

---

## 📌 Executive Summary

Modern financial crime investigators face massive volumes of pseudonymous blockchain transactions coupled with network-layer metadata (IPs, ports, ASNs, geographic routing). Hardcoded rule-based heuristics fail because sophisticated actors frequently alter transaction volumes, fan-out ratios, and peer routing.

**CryptoTrace AI** is an advanced hybrid machine-learning and forensic graph analytics pipeline that ingests multi-format transaction metadata (**CSV, JSON, XML**), correlates blockchain activity with network infrastructure, trains genuine supervised and unsupervised AI models (**XGBoost, Isolation Forest, GraphSAGE GNN**), generates **SHAP-quantified decision attributions**, and delivers a prioritized forensic triage queue via an interactive dashboard.

---

## 🏗️ Architecture & Data Pipeline

```
┌────────────────────────────────┐
│  CSV / JSON / XML Ingestion    │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ Canonical Validation & Clean   │
│ pandas / Polars / Schema Enforce│
└───────────────┬────────────────┘
                │
        ┌───────┴────────────────┐
        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ Blockchain Layer │    │  Network Layer   │
│ Amounts / Fees   │    │  IPs / Ports     │
│ Inputs / Outputs │    │  ASNs / GeoIP    │
│ Wallet Velocity  │    │  Infrastructure  │
└────────┬─────────┘    └────────┬─────────┘
         └───────────┬───────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ Feature Pipeline (Strict Temporal Order) │
│ No Future Lookahead / Anti-Leakage Split │
└────────────────────┬─────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌────────────────┐ ┌──────────┐ ┌────────────────┐
│  Supervised ML │ │ Anomaly  │ │    Graph ML    │
│    XGBoost     │ │Isolation │ │   GraphSAGE    │
│  P(Suspicious) │ │  Forest  │ │ Node Embeddings│
└────────┬───────┘ └────┬─────┘ └────────┬───────┘
         └───────────┬──┴────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ Multi-Modal Risk Scoring Engine (0-100)  │
│ 50% ML + 20% Anom + 20% Graph + 10% Behav│
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ SHAP Explainability & Evidence Packages  │
│ Top Quantified Risk Factors (JSON Output)│
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ Ranked Investigative Triage Dashboard   │
│ Streamlit / Interactive Plotly Networks  │
└──────────────────────────────────────────┘
```

---

## 🔬 Core AI / ML Models

CryptoTrace AI avoids single-model dependency by deploying a three-layer analytical framework:

| Model Layer | Algorithm | Input Dimension | Forensic Purpose | Primary Evaluation Metric |
| :--- | :--- | :--- | :--- | :--- |
| **Supervised Classifier** | **XGBoost** (Gradient Boosted Trees) | Multi-modal engineered feature matrix | Predict probability of illicit activity $P(\text{illicit})$ | **PR-AUC**, **Precision@100**, **Recall@100** |
| **Unsupervised Anomaly** | **Isolation Forest** | Behavioral velocity & fan-out statistics | Identify rare outliers & unseen anomalous transaction bursts | **Anomaly Score (0–100)** |
| **Graph Neural Network** | **GraphSAGE** | Heterogeneous Graph (Wallet, TX, IP, ASN) | Neighborhood representation learning & structural colocation | **Node Classification ROC-AUC** |
| **Explainability Engine** | **SHAP** (TreeExplainer) | Tree leaf paths & feature attributions | Provide local quantified evidence for human investigators | **Marginal Impact ($\phi_i$)** |

---

## 📊 Engineered Feature Schema

All features are engineered strictly in chronological order without lookahead data leakage:

1. **Transaction Topology**: `input_count`, `output_count`, `total_input_amount`, `total_output_amount`, `fee`, `fee_ratio`, `fan_out_ratio`, `output_entropy`, `output_amount_variance`.
2. **Wallet Historical Dynamics**: `wallet_tx_count`, `wallet_sent_count`, `wallet_recv_count`, `wallet_unique_ips`, `wallet_unique_asns`, `wallet_avg_sent_amount`.
3. **Temporal Velocity**: `wallet_txs_last_1h`, `wallet_txs_last_6h`, `wallet_txs_last_24h`, `time_since_prev_wallet_tx`, `burst_score`.
4. **Network & Infrastructure**: `ip_tx_count`, `ip_associated_wallets_count`, `is_standard_btc_port`, `shared_infrastructure_indicator`.
5. **Graph Topological Metrics**: `graph_degree`, `graph_in_degree`, `graph_out_degree`, `graph_pagerank`, `graph_2hop_neighbors`, `graph_3hop_neighbors`.

---

## 🚀 Quickstart & Offline Execution

### 1. Installation

```bash
git clone https://github.com/rajdeepcodeshere247/Crypto-Trace-AI.git
cd Crypto-Trace-AI
pip install -r requirements.txt
```

### 2. Generate Synthetic Blockchain & Network Data

```bash
python scripts/generate_dataset.py --transactions 12000 --wallets 1200 --ips 150
```

### 3. Ingest & Feature Extraction Pipeline

```bash
python scripts/prepare_data.py --input data/synthetic/transactions.csv
```

### 4. Train Multi-Modal Models

```bash
python scripts/train.py --model all
```

### 5. Benchmark & Model Evaluation

```bash
python scripts/evaluate.py
```

### 6. End-to-End Inference & Alert Generation

```bash
python scripts/predict.py --input data/synthetic/transactions.csv
```

### 7. Launch Interactive Forensic Dashboard

```bash
streamlit run dashboard/app.py
```

---

## 🌐 Multi-Page Forensic Dashboard

The Streamlit dashboard contains 8 dedicated investigative views:

1. **Overview**: High-level KPIs, activity timeline, risk tier breakdown, and behavioral archetype distribution.
2. **Alert Ranking & Triage**: Prioritized investigation queue with risk-tier filtering and real-time dossier previews.
3. **Transaction Explorer**: Deep inspection of raw inputs, outputs, miner fees, and network metadata.
4. **Wallet Investigation**: Longitudinal activity timeline, counterparty interactions, and velocity spikes.
5. **Network Graph Forensics**: Interactive 2D/3D Plotly heterogeneous network graph with 1-hop, 2-hop, and 3-hop ego expansion.
6. **Geographic & ASN Analysis**: Global transaction concentration choropleth and autonomous system hosting distribution.
7. **Model Explainability (SHAP)**: Waterfall decision decompositions and machine-readable JSON forensic evidence.
8. **Model Performance & Benchmarks**: Comparative evaluation matrices, PR curves, and ROC curves across all models.

---

## ⚖️ Ethical & Forensic Disclaimers

- **Investigative Prioritization**: Risk scores generated by CryptoTrace AI represent statistical prioritization metrics to aid human investigators; they do not constitute legal proof of criminality.
- **Contextual Network Evidence**: IP address and GeoIP correlations represent contextual network observations. IP addresses alone do not identify physical human individuals.
- **Defensive Research Only**: CryptoTrace AI is designed exclusively for authorized defensive research, compliance analytics, and financial forensics using public and synthetic datasets.
