# 📖 CryptoTrace AI Data Dictionary

This document specifies the canonical schema fields, data types, and engineered feature definitions.

---

## 1. Raw & Ingested Transaction Schema

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

## 2. Engineered Feature Taxonomy

| Feature | Category | Description |
| :--- | :--- | :--- |
| `fan_out_ratio` | Transaction | Ratio of output count to input count |
| `output_entropy` | Transaction | Shannon entropy across output value distribution |
| `output_amount_variance`| Transaction | Variance of output slices (peeling indicator) |
| `wallet_txs_last_1h` | Temporal | Count of transactions from wallet in past 1 hour |
| `wallet_txs_last_24h` | Temporal | Count of transactions from wallet in past 24 hours |
| `burst_score` | Temporal | Indicator of rapid-fire sub-minute transactions |
| `shared_infrastructure_indicator` | Network | Index of distinct wallets collocated on single IP |
| `wallet_unique_ips_count` | Network | Count of distinct IP hops utilized by wallet |
| `graph_pagerank` | Graph | Centrality score in heterogeneous transaction graph |
| `graph_2hop_neighbors` | Graph | Size of 2-hop neighborhood in network |
