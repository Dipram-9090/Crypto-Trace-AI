# CryptoTrace AI — REST API & CLI Documentation

## Standardized Response Envelope
All API endpoints follow a standardized JSON envelope structure:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "dataset_id": "transactions.csv",
    "timestamp": "2026-09-02T18:45:00.000000",
    "processing_time_ms": 12.5
  },
  "error": null
}
```

---

## API Endpoints

### 1. Ingest Dataset
- **`POST /api/blockchain/ingest`**
  - Ingest and index a DataFrame/dataset file.
  - Returns `validation_report`, total transactions, address profiles, and clusters.

### 2. Transaction Forensics
- **`GET /api/blockchain/transactions/:txid`**
  - Returns transaction details, UTXO outpoints, script types, and change output predictions.
- **`GET /api/blockchain/transactions/:txid/risk`**
  - Returns composite risk score (0-100), risk tier, and explainable forensic signals.

### 3. Address Intelligence
- **`GET /api/blockchain/addresses/:address`**
  - Returns profile, active balance, incoming/outgoing counts, first/last seen, and cluster ID.
- **`GET /api/blockchain/addresses/:address/graph`**
  - Returns k-hop ego network (nodes, links) around address.
- **`GET /api/blockchain/addresses/:address/timeline`**
  - Returns chronological activity history and transfer events.

### 4. Search & Fund Flow
- **`POST /api/blockchain/search`** (Body: `{"query": "..."}`)
  - Universal search resolving txid, address, cluster ID, or block height.
- **`POST /api/blockchain/path`** (Body: `{"source": "...", "destination": "..."}`)
  - Calculates directed fund flow paths with intermediary hops and transferred amounts.

### 5. Case Management & Reports
- **`POST /api/blockchain/cases`** (Body: `{"title": "...", "description": "..."}`)
  - Create new investigation case dossier.
- **`GET /api/blockchain/reports/:caseId`**
  - Generate full Markdown audit report for a case.

---

## Command-Line Interface (CLI)

```bash
# Ingest & Analyze Dataset
python src/cryptotrace/cli.py analyze data/sample/transactions.csv

# Inspect Transaction Details
python src/cryptotrace/cli.py transaction <txid>

# Inspect Address Profile
python src/cryptotrace/cli.py address <address>

# Query 2-Hop Graph Neighborhood
python src/cryptotrace/cli.py graph <address> --hops 2

# Inspect Risk Signals
python src/cryptotrace/cli.py risk <txid>

# Query Common-Input Address Cluster
python src/cryptotrace/cli.py cluster <address_or_cluster_id>

# Trace Fund Flow Paths
python src/cryptotrace/cli.py path <source_address> <destination_address>

# Universal Search
python src/cryptotrace/cli.py search <identifier>

# Export Case Forensic Report
python src/cryptotrace/cli.py report <case_id> --out report.md
```
