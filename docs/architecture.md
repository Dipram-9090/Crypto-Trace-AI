# 🏗️ CryptoTrace AI Architecture Specification

CryptoTrace AI is architected as an end-to-end, multi-tier forensic intelligence pipeline designed for financial forensics and blockchain compliance analytics.

---

## 1. System High-Level Topology

```
┌─────────────────────────────────────────────────────────────┐
│                       Data Ingestion                        │
│   CSV Parser     │     JSON Parser     │     XML Parser     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Canonical Normalization                  │
│       Schema Validation & Robust Type Casting (Polars/Pandas)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│   Blockchain Layer (On-chain)│ │ Network Layer (Off-chain)   │
│   Amounts, Fees, Scripts,    │ │ IPs, Ports, GeoIP, ASNs,    │
│   Inputs/Outputs, Wallets    │ │ Multi-wallet Colocation     │
└───────────────┬──────────────┘ └─────────────┬───────────────┘
                └──────────────┬───────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│        Temporal Feature Engineering (Anti-Leakage)          │
│   Rolling Window Velocity (1h, 6h, 24h, 7d) & Burst Indices │
└──────────────────────────────┬──────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌──────────────────┐ ┌───────────────────┐ ┌──────────────────┐
│ Supervised Trees │ │ Behavioral Anomaly│ │ Graph Neural Net │
│     XGBoost      │ │ Isolation Forest  │ │    GraphSAGE     │
└────────┬─────────┘ └─────────┬─────────┘ └────────┬─────────┘
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Modal Risk Scoring Engine                │
│    50% Supervised + 20% Anomaly + 20% Graph + 10% Behavior   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              SHAP Local Decision Attribution                │
│       Quantified Feature Positive/Negative Contributions    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Forensic Triage & Streamlit Dashboard             │
│    Ranked Alerts Queue, Subgraph Explorer, Geo Choropleth   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Layout & Dependency Direction

The project follows the strict Python Packaging Guide `src/` layout:

- **Dashboard UI** (`dashboard/`) consumes -> **Pipelines** (`src/cryptotrace/pipelines/`)
- **Pipelines** orchestrate -> **Models, Scoring, Graph** (`src/cryptotrace/models/`, `scoring/`, `graph/`)
- **Models & Scoring** consume -> **Features & Preprocessing** (`src/cryptotrace/features/`, `preprocessing/`)
- **Preprocessing** consumes -> **Ingestion** (`src/cryptotrace/ingestion/`)
