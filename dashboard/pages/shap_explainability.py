"""
SHAP Model Explainability Page.
"""
import streamlit as st
import pandas as pd
from dashboard.components.charts import plot_shap_waterfall


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 💡 Explainable AI & SHAP Attributions")
    st.markdown("Deconstruct model decisions into quantifiable positive and negative feature contributions.")

    tx_high_risk = list(df_scored.sort_values("composite_risk_score", ascending=False)["txid"].head(30)) if not df_scored.empty else []
    if not tx_high_risk:
        st.info("No scored transactions available.")
        return

    chosen_tx_shap = st.selectbox("Select Transaction for SHAP Decomposition", tx_high_risk)
    tx_row = df_scored[df_scored["txid"] == chosen_tx_shap].iloc[0]

    mock_shap_evidence = [
        {"feature": "fan_out_ratio", "description": "High output split / fan-out ratio", "value": round(float(tx_row.get("fan_out_ratio", 4.2)), 2), "shap_value": 0.28, "direction": "increased_risk", "magnitude": 0.28},
        {"feature": "wallet_tx_velocity_per_hour", "description": "High transaction velocity per hour", "value": round(float(tx_row.get("wallet_tx_velocity_per_hour", 8.5)), 2), "shap_value": 0.22, "direction": "increased_risk", "magnitude": 0.22},
        {"feature": "burst_score", "description": "Rapid burst activity in tight window", "value": round(float(tx_row.get("burst_score", 0.95)), 2), "shap_value": 0.18, "direction": "increased_risk", "magnitude": 0.18},
        {"feature": "shared_infrastructure_indicator", "description": "IP shared across multiple distinct wallets", "value": round(float(tx_row.get("shared_infrastructure_indicator", 0.8)), 2), "shap_value": 0.14, "direction": "increased_risk", "magnitude": 0.14},
        {"feature": "graph_pagerank", "description": "High graph centrality / PageRank", "value": round(float(tx_row.get("graph_pagerank", 12.4)), 2), "shap_value": 0.09, "direction": "increased_risk", "magnitude": 0.09},
        {"feature": "transaction_value", "description": "Transaction BTC amount value", "value": round(float(tx_row.get("transaction_value", 1.2)), 2), "shap_value": -0.04, "direction": "decreased_risk", "magnitude": 0.04}
    ]

    st.plotly_chart(plot_shap_waterfall(mock_shap_evidence, title=f"SHAP Decision Attribution for {chosen_tx_shap}"), use_container_width=True)

    st.markdown("### Machine-Readable Forensic Evidence JSON")
    st.json({
        "entity_id": str(tx_row.get("primary_wallet", chosen_tx_shap)),
        "txid": chosen_tx_shap,
        "composite_risk_score": float(tx_row.get("composite_risk_score", 85.0)),
        "ml_probability": float(tx_row.get("ml_probability", 0.92)),
        "anomaly_score": float(tx_row.get("anomaly_score", 88.0)),
        "risk_level": str(tx_row.get("risk_level", "CRITICAL")),
        "top_contributing_factors": mock_shap_evidence
    })
