# CryptoTrace AI — Forensic Methodology & Risk Scoring Engine

## Forensic Methodology & Evidence Taxonomy

To maintain evidentiary integrity in compliance with cybercrime and forensic audit standards, findings are categorized into four distinct classes:

| Class | Definition | Example |
|---|---|---|
| **OBSERVED FACTS** | Immutable, cryptographically verified on-chain data | Transaction hash, block height, timestamps, output value |
| **HEURISTIC INFERENCES** | Behavioral patterns derived from probabilistic rules | Common-Input Clusters, Peel Chains, Change Address prob |
| **ML ANOMALIES** | Statistical outliers detected by machine learning | Isolation Forest anomaly scores |
| **INVESTIGATOR NOTES** | Human analyst qualitative notes and hypotheses | Case annotations, evidence logs |

---

## 1. Address & Entity Clustering

### Common-Input Ownership Heuristic
- When multiple Bitcoin addresses are co-spent as inputs in a single multi-input transaction (`vin_1`, `vin_2`, ...), the engine connects these addresses as belonging to the same entity wallet cluster.
- **Evidential Distinction**: Clusters are labeled **HEURISTIC CLUSTER** (e.g., `CLUSTER_0001`) with a confidence level, not a confirmed physical legal identity.

---

## 2. Change Address Detection

The `ChangeAddressDetector` computes `change_probability` (0.0 to 1.0) using multiple forensic indicators:
1. **Self-Spending**: Output address matching an input address in the transaction.
2. **Script Type Matching**: Output script type matching the input script type (e.g., SegWit input to SegWit change).
3. **Round Value Payments**: Identifies round integer or standard decimal payment values (e.g., 1.0 BTC, 0.5 BTC) as merchant payments, leaving remainder as change.
4. **Address Freshness**: Distinguishes fresh HD wallet change addresses from heavily reused addresses.

---

## 3. Forensic Pattern Detection Heuristics

### Peel Chain Detection
- Identifies sequences of 1-to-2 output transactions where funds are incrementally peeled off to payment destinations while the remaining balance forwards to a series of fresh change addresses.
- Computes: `chain_length`, `initial_value`, `final_value`, and `value_decay_pct`.

### Mixing / CoinJoin Detection
- Detects multi-input multi-output transactions with high symmetry in output values (low coefficient of variation), equal output tiers, and high Shannon entropy.
- Labeled as **MIXING_LIKE_STRUCTURE** (explicitly not "confirmed mixer").

### High Fan-In & Fan-Out Analysis
- **Fan-In (Consolidation)**: Aggregation of 10+ funding sources into a single vault.
- **Fan-Out (Dispersion)**: Splitting of a single input across 10-25+ target addresses.

### Rapid Movement / High Velocity
- Tracks fund forwarding across consecutive hops with short inter-block or timestamp intervals (< 10 minutes).

### Dormant Address Activation
- Identifies long inactivity periods (> 90–180 days) followed by sudden high-value transfers.

---

## 4. Explainable Composite Risk Scoring

$$\text{Risk Score} = \min\left(100, w_{\text{heuristic}} \cdot S_{\text{heuristic}} + w_{\text{ml}} \cdot S_{\text{ml}} + w_{\text{graph}} \cdot S_{\text{graph}}\right)$$

### Risk Categories:
- **0–29**: `LOW`
- **30–59**: `MEDIUM`
- **60–79**: `HIGH`
- **80–100**: `CRITICAL`

Every evaluated entity includes explainable `signals` detailing severity, score contribution, and human-readable narratives.

---

## 5. Forensic Limitations & Disclaimers

> [!IMPORTANT]
> 1. **Pseudonymity**: Bitcoin addresses are cryptographic keys; an address does not prove real-world human identity.
> 2. **Heuristic Nature**: Clustering and change detection are probabilistic inferences.
> 3. **Analytical Indicators**: High risk scores and mixing patterns represent forensic anomalies, not legal proof of illegal activity.
