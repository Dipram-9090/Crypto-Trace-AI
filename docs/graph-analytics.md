# 🕸️ Heterogeneous Graph Analytics & Topology

CryptoTrace AI models the Bitcoin forensic ecosystem as a multi-relational, directed graph.

## 1. Node & Edge Ontology

- **Node Types**:
  - `Transaction`: Transaction hash entity with value, fee, and timestamp attributes.
  - `Wallet`: Bitcoin address entity with balance, degree, and transaction history.
  - `IP`: Network endpoint address with observed ports and geolocation attributes.
  - `ASN`: Autonomous System Number and network routing carrier.
  - `Country`: Geographic jurisdiction.

- **Edge Relationships**:
  - `INPUT_FROM`: Wallet $\to$ Transaction (spending BTC).
  - `OUTPUT_TO`: Transaction $\to$ Wallet (receiving BTC).
  - `OBSERVED_TRANSACTION`: IP $\to$ Transaction (broadcast source).
  - `BELONGS_TO`: IP $\to$ ASN (network infrastructure).
  - `LOCATED_IN`: IP $\to$ Country (spatial jurisdiction).
  - `TEMPORALLY_FOLLOWS`: Transaction $\to$ Transaction (temporal sequence).

---

## 2. Graph Centrality Metrics

1. **PageRank**: Measures structural influence and money-flow concentration across the global network.
2. **In-Degree & Out-Degree**: Distinguishes consolidation hubs (high in-degree) from mixing splitters (high out-degree).
3. **Sub-Graph Ego Extraction**: Rapid $k$-hop neighborhood retrieval for investigator deep-dives.
