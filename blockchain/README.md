# ⛓️ Blockchain Layer (`blockchain/`)

This directory contains all core blockchain-layer forensic logic for CryptoTrace AI:

- **`bitcoin/`**:
  - `transaction.py`: Directional multi-input multi-output Bitcoin transaction representations and fan-out calculation.
  - `block.py`: Bitcoin block header and payload models.
  - `utxo.py`: Unspent transaction output tracker for peeling chain and consolidation detection.
  - `scripts.py`: Locking script (`scriptPubKey`) parser for P2PKH, P2SH, SegWit (Bech32), and Taproot (Bech32m).
  - `parser.py`: Offline deserializer for raw transaction hex and JSON payloads.
- **`addresses/`**:
  - `validator.py`: Base58Check & Bech32 format validator.
  - `normalizer.py`: URI prefix stripping and whitespace normalizer.
  - `classifier.py`: Address script type classifier.
- **`rpc/`**:
  - `bitcoin_core.py`: Optional, offline-safe Bitcoin Core JSON-RPC node adapter.
