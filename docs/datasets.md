# 📊 Dataset Specifications & Supported Formats

CryptoTrace AI supports benchmark public datasets, offline enrichment databases, and high-fidelity synthetic network simulations.

---

## 1. Supported Public Benchmarks

1. **Elliptic Bitcoin Dataset**:
   - Location: `data/raw/elliptic/`
   - Files: `elliptic_txs_features.csv`, `elliptic_txs_classes.csv`, `elliptic_txs_edgelist.csv`
   - Scope: 203k transaction nodes across 49 time steps with 166 structural features.

2. **Elliptic++ Extended Dataset**:
   - Location: `data/raw/ellipticpp/`
   - Scope: Dual transaction and wallet graphs with `AddrAddr`, `AddrTx`, and `TxAddr` edgelists.

3. **BitcoinHeist Ransomware Dataset**:
   - Location: `data/raw/bitcoinheist/`
   - Files: `BitcoinHeistData.csv`
   - Scope: Address-level graph metrics (`length`, `weight`, `count`, `looped`, `neighbors`, `income`) labeled by ransomware family.

4. **GeoLite2 Databases (MaxMind)**:
   - Location: `data/external/geoip/`
   - Files: `GeoLite2-City.mmdb`, `GeoLite2-ASN.mmdb`

5. **CryptoTrace Synthetic Network Simulation**:
   - Location: `data/synthetic/`
   - Files: `transactions.csv`, `network_events.csv`, `wallets.csv`, `ip_wallet_mapping.csv`, and compressed Parquet equivalents.
