# 🌐 Network-Layer Correlation & Telemetry Analysis

CryptoTrace AI correlates on-chain transactions with observed P2P network layer metadata.

## 1. Multi-Modal Correlation Topology

```
+--------------------------+          +--------------------------+
|     Blockchain Layer     |          |      Network Layer       |
|  (TXID, Wallets, BTC)    |          |  (IP, Port, ASN, Geo)    |
+-------------+------------+          +------------+-------------+
              |                                    |
              +-----------------+------------------+
                                |
                                v
               [ Cross-Modal Correlation Engine ]
                                |
             +------------------+------------------+
             |                                     |
             v                                     v
   [ Shared Infrastructure ]             [ Multi-IP Hopping ]
   (1 IP -> Many Wallets)                (1 Wallet -> Many IPs)
```

## 2. Investigative Network Metrics

1. **Shared Infrastructure Index**:
   Measures whether multiple distinct wallet entities broadcast transactions from the exact same IP address or ASN within tight time windows.
2. **IP Diversity & Hopping Index**:
   Tracks whether an individual wallet address rapidly shifts across VPN/Tor hosting subnets between consecutive transactions.
3. **P2P Broadcast Port Fingerprinting**:
   Detects non-standard ports, standard Bitcoin P2P port (`8333`), and known proxy listeners (`9050`, `9150`, `4444`).
