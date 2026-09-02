<div align="center">

# 🛡️ CryptoTrace AI
### Enterprise Multi-Modal Graph & Machine Learning Forensic Analytics for Bitcoin

[![CI Pipeline](https://github.com/rajdeepcodeshere247/Crypto-Trace-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/rajdeepcodeshere247/Crypto-Trace-AI/actions)
[![Security Scan](https://github.com/rajdeepcodeshere247/Crypto-Trace-AI/actions/workflows/security.yml/badge.svg)](https://github.com/rajdeepcodeshere247/Crypto-Trace-AI/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Offline-First](https://img.shields.io/badge/Architecture-Offline--First-blueviolet.svg)](docs/security.md)

<p align="center">
  <b>Production-grade, offline-first Bitcoin transaction and network-layer forensic intelligence platform.</b><br>
  Combines multi-format ingestion (CSV, JSON, XML), heterogeneous graph construction, supervised gradient boosting, unsupervised anomaly detection, inductive Graph Neural Networks (GraphSAGE), and SHAP decision attribution.
</p>

[Key Features](#-key-features) •
[Architecture](#-system-architecture) •
[Datasets](#-supported-datasets) •
[Model Benchmarks](#-model-benchmarks) •
[Quickstart](#-quickstart-guide) •
[Dashboard](#-interactive-forensic-dashboard) •
[Documentation](#-documentation)

---

</div>

## 🌟 Key Features

- **Multi-Format Ingestion & Validation**: Ingests bulk Bitcoin transactions and network broadcast events from CSV, JSON, and XML with schema validation and deduplication.
- **Cross-Modal Blockchain/Network Correlation**: Maps transaction hashes and wallet clusters to broadcasting IP addresses, Autonomous Systems (ASNs), and geographic jurisdictions without lookahead leakage.
- **Heterogeneous Forensic Graph**: Builds directed multi-relational graphs across Transactions, Wallets, IPs, ASNs, and Countries using NetworkX and PyTorch.
- **Hybrid Machine Learning Pipeline**:
  - **Supervised XGBoost**: Primary transaction classification with strict temporal train/val/test splitting (**PR-AUC: 0.9985, Recall@100: 77.5%**).
  - **Isolation Forest**: Unsupervised behavioral anomaly detector for identifying novel peeling and mixing patterns.
  - **Inductive GraphSAGE GNN**: Deep representation learning over multi-hop relational transaction neighborhoods.
  - **Behavioral Clustering (DBSCAN + PCA)**: Latent cluster discovery identifying rapid mixing rings and exchange hot wallets.
  - **BitcoinHeist Ransomware Classifier**: Dedicated address graph classifier detecting ransomware families.
- **Explainable AI (SHAP)**: Quantifiable game-theoretic feature attribution producing human-readable explanations and machine-readable evidence JSON dossiers.
- **Multi-Modal Risk Scoring Engine**: Configurable composite scoring formula combining ML probability, anomaly score, graph topology, and behavioral indicators.
- **High-Performance Storage**: Columnar compressed Parquet storage with zero-copy embedded **DuckDB** analytical querying.
- **Interactive Multi-Page Streamlit Dashboard**: 10 distinct forensic views including Alert Triage, Network Graph, SHAP Explainability, Geographic Map, Behavioral PCA, and DuckDB SQL Console.

---

## 🏛️ System Architecture

```
                                  RAW DATA (CSV / JSON / XML)
                                              |
                                              v
                              +-------------------------------+
                              |    Ingestion & Validation     |
                              +---------------+---------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
         [ Blockchain Layer ]                                  [ Network Layer ]
     TXID, Wallets, Amounts, Fees                          IP, Port, Timing, ASN, Geo
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                              +-------------------------------+
                              | Cross-Modal Correlation Engine|
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |  Heterogeneous Graph Builder  |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Anti-Leakage Feature Builder  |
                              +---------------+---------------+
                                              |
                 +----------------------------+----------------------------+
                 |                            |                            |
                 v                            v                            v
        [ XGBoost Classifier ]      [ Isolation Forest ]          [ GraphSAGE GNN ]
          Supervised PR-AUC           Anomaly Detection            Graph Topology
                 |                            |                            |
                 +----------------------------+----------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |   Multi-Modal Risk Engine     |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |   SHAP Decision Attribution   |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Ranked Investigative Alerts   |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Streamlit Forensic Dashboard  |
                              +-------------------------------+
```

---

## 📊 Supported Datasets

| Dataset | Type | Role | Priority |
| :--- | :--- | :--- | :--- |
| **Elliptic Bitcoin Dataset** | Real-world Graph | Main illicit/licit transaction classifier (203k TXs) | ⭐⭐⭐⭐⭐ |
| **Elliptic++** | Extended Graph | Dual transaction and wallet address graphs + GNN | ⭐⭐⭐⭐⭐ |
| **BitcoinHeist** | Ransomware Data | Address-level graph features & ransomware families | ⭐⭐⭐⭐ |
| **GeoLite2 (MaxMind)** | Network DB | IP-to-Country and IP-to-ASN local enrichment | ⭐⭐⭐⭐ |
| **CryptoTrace Synthetic** | P2P Simulation | Multi-layer network events, wallets & timing | ⭐⭐⭐⭐⭐ |

---

## 📈 Model Benchmarks

Evaluation on strictly held-out forward-looking temporal test partitions:

| Model | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | Precision@100 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Baseline)** | 0.2667 | 0.8062 | 0.4008 | 0.4449 | 0.8994 | - |
| **Random Forest (Baseline)** | 0.9921 | 0.9690 | 0.9804 | 0.9967 | 0.9997 | - |
| **XGBoost (Primary Classifier)** | **0.9921** | **0.9767** | **0.9844** | **0.9985** | **0.9999** | **1.0000** |
| **Isolation Forest (Anomaly)** | 0.2500 | 0.0078 | 0.0150 | 0.1587 | 0.7937 | - |
| **BitcoinHeist Ransomware XGBoost**| **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | - |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Linux, macOS, or Windows

### Installation

```bash
# Clone the repository
git clone https://github.com/rajdeepcodeshere247/Crypto-Trace-AI.git
cd Crypto-Trace-AI

# Install package and dependencies in development mode
pip install -e .[dev]
```

### Complete Pipeline Run

```bash
# 1. Generate multi-layer synthetic datasets
make generate

# 2. Extract features, build graph, and serialize Parquet
make prepare

# 3. Train all models (XGBoost, Isolation Forest, GraphSAGE, Clustering, Ransomware)
make train

# 4. Evaluate models on temporal test split
make evaluate

# 5. Run inference and generate prioritized alert queue
make predict

# 6. Launch forensic analytics dashboard
make dashboard
```

---

## 🖥️ Interactive Forensic Dashboard

Launch the interactive investigation suite:

```bash
streamlit run dashboard/app.py
```

### Included Dashboard Views:
1. **Overview**: KPI cards, transaction breakdown, and behavioral archetype distributions.
2. **Alert Ranking & Triage**: Prioritized leads queue with interactive dossier cards.
3. **Transaction Explorer**: Atomic transaction inspection and network transmission properties.
4. **Wallet Forensics**: Longitudinal counterparty history and infrastructure colocation.
5. **Network Graph**: 2D interactive sub-graph ego-network explorer.
6. **Geographic & ASN Analysis**: World choropleth map and top hosting ASNs.
7. **Behavioral Clustering & PCA**: 2D PCA cluster projection of discovered mixing rings.
8. **DuckDB SQL Analytics**: In-memory SQL console and wallet aggregations.
9. **Model Explainability (SHAP)**: Waterfall bar charts and decision factors.
10. **Model Benchmarks**: Comparative precision-recall curves and ROC metrics.

---

## 📚 Documentation

- [Architecture Design & Pipeline Flow](docs/architecture.md)
- [Bitcoin Blockchain & UTXO Model](docs/blockchain.md)
- [Network Layer Telemetry & Correlation](docs/network-correlation.md)
- [Machine Learning & GNN Pipelines](docs/ml-pipeline.md)
- [Heterogeneous Graph Analytics](docs/graph-analytics.md)
- [Explainability & SHAP Evidence](docs/explainability.md)
- [Dataset Specifications & Schemas](docs/data-dictionary.md)
- [Security Model & Offline Air-Gapping](docs/security.md)
- [Development & Testing Guide](docs/development.md)

---

## 📄 License

CryptoTrace AI is licensed under the [Apache License 2.0](LICENSE).
