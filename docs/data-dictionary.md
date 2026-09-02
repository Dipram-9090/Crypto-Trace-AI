# 📖 CryptoTrace AI Multi-Dataset Data Dictionary

This document specifies the canonical schema fields, public dataset mappings (Elliptic, Elliptic++, BitcoinHeist, GeoLite2), synthetic network telemetry, and storage format specifications.

---

## 1. Multi-Dataset Architecture Overview

| Dataset | Format / Location | Role & Application | Primary Model |
| :--- | :--- | :--- | :--- |
| **Elliptic Bitcoin Dataset** | CSV (`data/raw/elliptic/`) | Illicit / Licit transaction node classification | Supervised XGBoost, Random Forest |
| **Elliptic++** | CSV (`data/raw/ellipticpp/`) | Dual Wallet & Transaction graph analytics | GraphSAGE GNN, PageRank, Degree Centrality |
| **BitcoinHeist** | CSV (`data/raw/bitcoinheist/`) | Address-level ransomware detection | Ransomware XGBoost Classifier |
| **GeoLite2 (MaxMind)** | MMDB/CSV (`data/external/geoip/`) | IP-to-Country and IP-to-ASN network enrichment | Deterministic GeoIP & Proxy Resolver |
| **CryptoTrace Synthetic Network** | CSV/Parquet (`data/synthetic/`) | IP/port/timing P2P network telemetry bridge | Isolation Forest, Behavioral Clusterer |

---

## 2. Canonical Transaction Schema (Network + Blockchain Unified)

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `txid` | `string` | Unique transaction identifier hash | `TX_000142_9182` |
| `timestamp` | `string (ISO)` | Transaction broadcast timestamp | `2026-01-01 14:22:10` |
| `src_ip` | `string (IPv4)` | Observed broadcast source IP address | `185.220.101.5` |
| `dst_ip` | `string (IPv4)` | Peer peer-to-peer receiving node IP | `51.15.89.2` |
| `src_port` | `integer` | Originating network port | `54321` |
| `dst_port` | `integer` | Destination network port (default: 8333) | `8333` |
| `input_addresses` | `list[string]` | Array of sending Bitcoin addresses | `["1BTC001a", "1BTC002b"]` |
| `output_addresses` | `list[string]` | Array of receiving Bitcoin addresses | `["1BTC003c"]` |
| `input_amounts` | `list[float]` | Array of input BTC amounts | `[1.45, 0.55]` |
| `output_amounts` | `list[float]` | Array of output BTC amounts | `[1.98]` |
| `fee` | `float` | Miner transaction fee in BTC | `0.02` |
| `script_type` | `string` | Bitcoin script encoding (`p2pkh`, `p2wpkh`, etc.) | `p2wpkh` |
| `src_country` | `string` | Resolved country name from GeoLite2 | `Netherlands` |
| `src_asn` | `string` | Autonomous System Number of source IP | `AS13335` |
| `label` | `integer` | Ground truth label (0: Licit, 1: Illicit, 2: Unknown) | `1` |
| `entity_type` | `string` | Behavioral profile archetype | `SUSPICIOUS_ACTOR` |

---

## 3. BitcoinHeist Ransomware Feature Schema

| Field | Type | Description |
| :--- | :--- | :--- |
| `address` | `string` | Bitcoin address identifier |
| `length` | `integer` | Length of transaction chain from address |
| `weight` | `float` | Fractional transaction output weight |
| `count` | `integer` | Number of distinct transaction inputs/outputs |
| `looped` | `integer` | Number of cyclic loops back to address |
| `neighbors` | `integer` | Degree / neighbor count in address subgraph |
| `income` | `float` | Total satoshis transacted through address |
| `is_ransomware`| `integer` | Binary indicator (1: Ransomware family, 0: Licit/White) |

---

## 4. Storage & Query Optimization

- **Columnar Compressed Parquet (`data/processed/*.parquet`)**: High-throughput storage using Snappy compression with PyArrow and Polars engines for 10x faster analytical reads.
- **DuckDB Analytical Views**: Zero-copy in-memory SQL execution engine for sub-second wallet aggregation, infrastructure concentration analysis, and complex window operations.
