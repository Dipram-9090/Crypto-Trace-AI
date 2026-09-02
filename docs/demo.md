# 🎬 CryptoTrace AI Demo Guide

Follow these steps for a live demonstration of CryptoTrace AI:

---

## 1. Quick Terminal Setup

```bash
# 1. Generate 3,000 synthetic multi-modal transactions
python scripts/generate_synthetic_data.py --transactions 3000

# 2. Extract features and construct forensic graph
python scripts/prepare_data.py

# 3. Train all AI/ML models (XGBoost, Isolation Forest, GraphSAGE)
python scripts/train.py --model all

# 4. Run end-to-end inference and alert ranking
python scripts/predict.py

# 5. Launch dashboard
streamlit run dashboard/app.py
```

---

## 2. Interactive Presentation Walkthrough

1. **Executive Dashboard**: Open `Overview` to show total processed transactions, active wallets, monitored IPs, and risk distributions.
2. **Prioritized Alert Triage**: Navigate to `Alert Triage`, select a `CRITICAL` alert, and display the composite score breakdown.
3. **SHAP Decision Attribution**: Open `SHAP Explainability` to demonstrate why the AI flagged the entity (e.g. output fan-out, velocity spike, shared IP colocation).
4. **Forensic Graph Visualizer**: Open `Network Graph` to explore 2-hop neighbor relationships connecting the suspicious wallet to observed IPs and ASNs.
5. **Model Benchmarking**: Review `Model Benchmarks` comparing XGBoost PR-AUC (0.995) against baseline classifiers.
