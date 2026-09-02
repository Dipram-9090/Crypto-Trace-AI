# 💡 Explainable AI (XAI) & Decision Decomposition

CryptoTrace AI provides transparent, quantifiable decision attribution for every scored entity and transaction lead.

---

## 1. SHAP (SHapley Additive exPlanations)

Using game-theoretic TreeExplainer formulations, the model calculates exact feature contributions ($s_i \in \mathbb{R}$) for every prediction:

$$\hat{y} = \phi_0 + \sum_{i=1}^{M} \phi_i$$

Where:
- $\phi_0$: Base expectation rate of illicit activity in the training set.
- $\phi_i > 0$: Feature $i$ pushed the risk score higher (e.g., elevated fan-out ratio, high velocity).
- $\phi_i < 0$: Feature $i$ pushed the risk score lower (e.g., standard fee, low entropy).

---

## 2. Machine-Readable Forensic Dossier Output

Each investigative alert generates a structured JSON dossier formatted for compliance audits, judicial evidence packages, and investigator review:

```json
{
  "alert_id": "ALERT_0042",
  "txid": "TX_90182_9281",
  "primary_wallet": "1BTC001928a",
  "composite_risk_score": 88.5,
  "risk_level": "CRITICAL",
  "confidence": 0.95,
  "top_features": [
    {
      "feature": "fan_out_ratio",
      "description": "High output split / fan-out ratio (layering indicator)",
      "value": 6.8,
      "shap_value": 0.28,
      "direction": "increased_risk"
    }
  ]
}
```
