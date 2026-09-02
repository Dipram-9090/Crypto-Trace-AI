# ⛓️ Bitcoin Blockchain Layer & UTXO Analysis

CryptoTrace AI treats the Bitcoin blockchain as a directional, multi-input, multi-output value transfer graph.

## 1. UTXO Transaction Model

Unlike account-based ledgers (e.g., Ethereum), Bitcoin transactions consume previously unspent transaction outputs (**UTXOs**) and produce new UTXOs:
- **Inputs ($\text{vin}$)**: References to previous transaction hashes (`txid`) and output indices (`vout`).
- **Outputs ($\text{vout}$)**: Value amounts in BTC / satoshis coupled with locking script public keys (`scriptPubKey`).
- **Miner Fee**: Implicitly calculated as $\text{Fee} = \sum \text{Inputs} - \sum \text{Outputs}$.

---

## 2. Supported Script Encodings

| Script Type | Standard Prefix | Description | Forensic Significance |
| :--- | :--- | :--- | :--- |
| **P2PKH** | `1...` | Pay-to-PubKey-Hash (Legacy Base58Check) | Standard legacy transfers |
| **P2SH** | `3...` | Pay-to-Script-Hash | Multisig / Escrows / Mixers |
| **P2WPKH** | `bc1q...` | Native SegWit v0 (Bech32) | Modern exchange & user wallets |
| **P2WSH** | `bc1q...` (62 chars) | SegWit Script Hash | Complex institutional multisig |
| **P2TR** | `bc1p...` | Taproot v1 (Bech32m, Schnorr) | Privacy-enhanced spending |

---

## 3. Heuristic Clustering Principles

1. **Common-Input-Ownership (Multi-Input Heuristic)**:
   If a transaction has multiple inputs $[w_1, w_2, \dots, w_k]$, all signing addresses are presumed to be controlled by the same wallet entity.
2. **Peeling Chain Detection**:
   Successive single-input, two-output transactions where one output is a large whole amount and the other is a small change amount transferred in quick succession.
