# 🔒 Security Model & Air-Gapping Architecture

CryptoTrace AI is engineered as an **offline-first, zero-trust analytical environment**.

---

## 1. Offline-First Guarantee

- **No Remote Telemetry**: The system operates with zero external network phone-homes or cloud dependencies.
- **Air-Gap Compatibility**: All ML models, feature encoders, and GeoIP lookup tables run locally within air-gapped forensic environments.
- **Adapter Isolation**: External blockchain nodes (Bitcoin Core RPC) and remote databases are strictly optional and encapsulated behind offline fallbacks.

---

## 2. Privacy & Data Integrity

- **No PII Collection**: All transactions and entity identifiers are pseudonymized blockchain hashes and IP addresses.
- **SHA-256 Audit Logging**: All investigative lead reports and scoring executions are timestamped and signed with cryptographic hashes.
