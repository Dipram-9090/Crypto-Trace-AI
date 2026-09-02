# ⚙️ Backend & Data Engineering Layer (`backend/`)

This directory contains the data engineering, ingestion, correlation, and analytical backend engines:

- **Ingestion & Validation**:
  - `csv_loader.py`, `json_loader.py`, `xml_loader.py`: High-throughput multi-format parsers.
  - `elliptic.py`, `ellipticpp.py`, `bitcoinheist.py`: Public benchmark dataset loaders.
  - `network_bridge.py`: Synthesizes realistic P2P network telemetry over on-chain records.
- **Cross-Modal Correlation Engine**:
  - `transaction_ip.py`: Correlates transaction broadcasts with observed network endpoints.
  - `wallet_ip.py`: Detects shared infrastructure and multi-IP hopping.
  - `temporal.py`: Cross-correlates confirmation intervals with network propagation delays.
  - `entity_resolution.py`: Merges multi-input clusters and co-located network identities.
- **Storage & In-Memory Analytics Engine**:
  - `duckdb_engine.py`: Zero-copy analytical SQL engine for fast wallet summaries and ASN concentration queries.
  - `parquet_io.py`: Compressed Snappy Parquet storage for high-throughput feature vectors.
- **Risk Scoring & Evidence Engine**:
  - `risk_engine.py`: Composite risk calculator combining ML probability, anomaly score, and graph topology.
  - `confidence.py`: Multi-modal consensus confidence evaluator.
  - `alert_generator.py`: Structured forensic dossier and alert lead generator.
