# 🛡️ Threat Model & Adversarial Evasion Analysis

CryptoTrace AI is designed to counter common adversarial obfuscation tactics used in Bitcoin money laundering.

---

## 1. Modeled Adversarial Vectors

### 1.1 Peeling Chains & Layering
- **Adversary Action**: Splitting large amounts into repeated small transactions across dozens of intermediary addresses.
- **Countermeasure**: High output entropy and amount variance features combined with 2-hop neighborhood clustering in GraphSAGE.

### 1.2 IP Hopping & VPN / Tor Exit Rotation
- **Adversary Action**: Changing broadcast IP per transaction to mask node location.
- **Countermeasure**: `wallet_unique_ips_count` and `wallet_unique_asns_count` features penalize high-frequency infrastructure hopping.

### 1.3 Rapid-Fire Burst Transfers
- **Adversary Action**: Automated script execution broadcasting transactions within seconds.
- **Countermeasure**: Sub-minute `burst_score` and rolling window velocity counters (1h, 6h, 24h).
