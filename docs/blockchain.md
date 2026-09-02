# CryptoTrace AI — Bitcoin Protocol & Blockchain Engine Documentation

## Overview
CryptoTrace AI implements a production-grade, modular, offline-first Bitcoin transaction forensics engine designed for law enforcement, blockchain analysts, and cybercrime investigation units.

---

## 1. Bitcoin Protocol Support

### Transaction Models & Inputs/Outputs
- **`BitcoinTransaction`**: Full transaction abstraction encapsulating `txid`, `version`, `locktime`, `vsize`, `fee`, `fee_rate` (sat/vB), `timestamp`, `block_height`, and collections of `TxInput` and `TxOutput`.
- **`TxInput` (vin)**: Tracks previous outpoint reference (`prev_txid:vout`), signature script (`script_sig`), sequence number, witness items, and input address attribution.
- **`TxOutput` (vout)**: Tracks destination address, transfer value in BTC / satoshis, `scriptPubKey` bytecode, script type classification, `OP_RETURN` payload parsing, and change address indicators.

### Script Types & Opcode Classification
The engine inspects and classifies Bitcoin script types without external network services:
- **P2PKH (Pay-to-Public-Key-Hash)**: Standard legacy scripts (`OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG`).
- **P2SH (Pay-to-Script-Hash)**: Script hash outputs (`OP_HASH160 <scriptHash> OP_EQUAL`).
- **P2WPKH (Native SegWit v0)**: 20-byte witness public key hashes (`bc1q...`).
- **P2WSH (Native SegWit v0 Script)**: 32-byte witness script hashes.
- **P2TR (Taproot BIP 341/342)**: 32-byte witness v1 outputs (`bc1p...`).
- **OP_RETURN**: Metadata outputs; safely extracts string and hex payloads without throwing exceptions.
- **Multisig**: Standard `m-of-n` multisig patterns (`OP_CHECKMULTISIG`).

### Address Validation & Classification
- **Base58Check**: Offline double-SHA256 checksum verification for Legacy (`1...`), Script (`3...`), and Testnet (`m...`, `n...`, `2...`) addresses.
- **Bech32 & Bech32m**: Polymod checksum verification according to BIP 173 and BIP 350.

---

## 2. UTXO Ledger & Fee Engine (`UTXOSet`)

The in-memory UTXO engine maintains:
- **Outpoint Tracking**: Keyed by `txid:vout`.
- **Spending Lifecycle**: Marks outpoints as spent when referenced by subsequent transaction inputs, logging `spent_in_txid` and `spent_at`.
- **Double-Spend Detection**: Automatically flags and logs any outpoint referenced for spending more than once.
- **Balance Calculation**: Accurately aggregates unspent output balances per address across blocks.
- **Fee Calculation**: Calculates `fee = total_input_amount - total_output_amount` when historical inputs are present in the dataset.

---

## 3. Schema Normalization & Offline Ingestion

Heterogeneous datasets (CSV, JSON, JSONL, Parquet) with varied column naming conventions are automatically mapped:
- `txid` / `transaction_id` / `hash` -> `txid`
- `from_address` / `sender` / `input_address` / `vin` -> `input_addresses`
- `to_address` / `receiver` / `output_address` / `vout` -> `output_addresses`
- `amount` / `value` / `output_amounts` -> `output_amounts`
- `fee` / `tx_fee` -> `fee`
- `timestamp` / `date` / `block_time` -> `timestamp`

Every ingestion produces a `DatasetValidationReport` detailing total records, valid/invalid records, duplicates, detected schema mappings, and dataset isolation ID (`dataset_id`).

---

## 4. Bitcoin Core JSON-RPC Adapter

Configured via environment variables:
```bash
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=rpcuser
BITCOIN_RPC_PASSWORD=rpcpassword
BITCOIN_RPC_ENABLED=false
```
When Bitcoin Core is offline or unreachable, the client safely falls back to offline dataset mode without hanging or crashing.
