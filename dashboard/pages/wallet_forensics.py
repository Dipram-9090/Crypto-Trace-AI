"""
Wallet Longitudinal Forensics Page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components.tables import render_metric_card


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 💼 Wallet Longitudinal Forensics")
    st.markdown("Track historical counterparty interactions, velocity spikes, and network infrastructure colocation.")

    wallets = sorted(list(set(df_scored["primary_wallet"].dropna()))) if not df_scored.empty else []
    if not wallets:
        st.info("No wallet data available.")
        return

    chosen_wallet = st.selectbox("Select Target Wallet Address", wallets[:100])
    w_df = df_scored[df_scored["primary_wallet"] == chosen_wallet].sort_values("datetime")

    wcol1, wcol2, wcol3 = st.columns(3)
    with wcol1: render_metric_card("Associated Transactions", f"{len(w_df)}", "Observed records")
    with wcol2:
        unique_w_ips = len(set(w_df["src_ip"].dropna()))
        render_metric_card("Associated IPs", f"{unique_w_ips}", "Infrastructure hopping")
    with wcol3:
        max_risk = w_df["composite_risk_score"].max() if "composite_risk_score" in w_df.columns else 0.0
        render_metric_card("Peak Risk Score", f"{max_risk:.1f} / 100", "Maximum observed tier")

    st.markdown("### Transaction Timeline & Value Flow")
    if "datetime" in w_df.columns and "transaction_value" in w_df.columns:
        fig_time = px.line(w_df, x="datetime", y="transaction_value", markers=True, title=f"Activity History for {chosen_wallet}")
        fig_time.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"))
        st.plotly_chart(fig_time, use_container_width=True)
