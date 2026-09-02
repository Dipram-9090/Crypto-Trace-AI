# CryptoTrace AI Synthetic Forensic Datasets

This directory contains realistic, synthetic Bitcoin transaction datasets for offline forensic testing, benchmark validation, and demonstration.

## Files
- `transactions.csv`: Tabular format with JSON-encoded address and amount lists.
- `transactions.json`: Standard JSON array of transaction objects.
- `transactions.jsonl`: Line-delimited JSON format for streaming ingestion.

## Synthetic Typologies Included
1. **Normal P2P**: 1-input to 2-output standard payments with change.
2. **High Fan-In**: 10-input consolidation into a single master vault.
3. **High Fan-Out**: 1-input dispersion across 15 target addresses.
4. **Rapid Movement**: Funds relayed across 5 consecutive hops within 10 minutes (high velocity).
5. **Peel Chain**: 5 consecutive peeling steps (large payment + decaying change).
6. **Mixing-Like Structure**: CoinJoin-style 5-input, 5-output structure with equal amounts and high entropy.
7. **Dormant Activation**: Address inactive for >200 days with sudden 50 BTC transfer.
8. **Common-Input Cluster**: Multi-input spending linking 3 addresses to a single entity.

*All data is synthetic and non-attributable to real persons.*
