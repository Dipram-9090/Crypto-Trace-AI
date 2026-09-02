"""
Overview & Executive Forensic Summary Page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components.tables import render_metric_card
from dashboard.components.charts import plot_risk_distribution_pie


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 📊 Executive Forensic Summary")
    st.markdown("Telemetry across Bitcoin transaction activity and observed network layer metadata.")

    col1, col2, col3, col4, col5 = st.columns(5)
    total_tx = len(df_scored)
    unique_wallets = len(set(df_scored["primary_wallet"].dropna())) if "primary_wallet" in df_scored.columns else 0
    unique_ips = len(set(df_scored["src_ip"].dropna())) if "src_ip" in df_scored.columns else 0
    crit_alerts = len(df_scored[df_scored["risk_level"] == "CRITICAL"]) if "risk_level" in df_scored.columns else 0
    high_alerts = len(df_scored[df_scored["risk_level"] == "HIGH"]) if "risk_level" in df_scored.columns else 0

    with col1: render_metric_card("Total Transactions", f"{total_tx:,}", "Canonical records")
    with col2: render_metric_card("Monitored Wallets", f"{unique_wallets:,}", "Unique addresses")
    with col3: render_metric_card("Observed IPs", f"{unique_ips:,}", "Network endpoints")
    with col4: render_metric_card("Critical Alerts", f"{crit_alerts:,}", "Risk score ≥ 80")
    with col5: render_metric_card("High Risk Alerts", f"{high_alerts:,}", "Risk score 60 - 79")

    st.markdown("### Risk Tier & Behavioral Distribution")
    rcol1, rcol2 = st.columns([1, 1])
    with rcol1:
        if "risk_level" in df_scored.columns:
            st.plotly_chart(plot_risk_distribution_pie(df_scored), use_container_width=True)
    with rcol2:
        if "entity_type" in df_scored.columns:
            ent_counts = df_scored["entity_type"].value_counts().reset_index()
            ent_counts.columns = ["Archetype", "Count"]
            fig_bar = px.bar(ent_counts, x="Archetype", y="Count", color="Archetype", title="Transactions by Behavioral Archetype")
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
