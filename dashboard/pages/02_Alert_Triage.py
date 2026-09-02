"""
Alert Ranking & Investigative Triage Page.
"""
import streamlit as st
import pandas as pd
import networkx as nx
from dashboard.components.tables import render_risk_badge
from dashboard.components.graph_view import plot_forensic_subgraph


def render_page(df_scored: pd.DataFrame, G_forensic: nx.DiGraph):
    st.markdown("## 🚨 Ranked Investigative Leads")
    st.markdown("Prioritized triage queue combining XGBoost, Isolation Forest, GraphSAGE, and network telemetry.")

    fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
    with fcol1: tier_filter = st.selectbox("Filter Risk Tier", ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with fcol2: entity_filter = st.selectbox("Entity Type", ["ALL", "Wallet", "Transaction"])
    with fcol3: search_query = st.text_input("🔍 Search Wallet, TXID, IP or ASN", "")

    filtered_df = df_scored.copy()
    if tier_filter != "ALL":
        filtered_df = filtered_df[filtered_df["risk_level"] == tier_filter]
    if search_query.strip():
        q = search_query.strip().lower()
        mask = (
            filtered_df["txid"].str.lower().str.contains(q) |
            filtered_df["src_ip"].str.lower().str.contains(q) |
            filtered_df["primary_wallet"].astype(str).str.lower().str.contains(q) |
            filtered_df["src_asn"].astype(str).str.lower().str.contains(q)
        )
        filtered_df = filtered_df[mask]

    st.markdown(f"**Showing {len(filtered_df):,} matching leads** (Sorted by Composite Risk Score)")
    display_cols = ["txid", "primary_wallet", "composite_risk_score", "risk_level", "ml_probability", "anomaly_score", "graph_score", "src_ip", "src_country", "entity_type"]
    avail_cols = [c for c in display_cols if c in filtered_df.columns]

    st.dataframe(filtered_df[avail_cols].sort_values("composite_risk_score", ascending=False).head(100), use_container_width=True, height=380)

    st.markdown("---")
    st.markdown("### 🔍 Forensic Deep-Dive Dossier")
    if not filtered_df.empty:
        top_txids = list(filtered_df.sort_values("composite_risk_score", ascending=False)["txid"].head(50))
        selected_txid = st.selectbox("Select Transaction Dossier to Inspect", top_txids)
        row_data = filtered_df[filtered_df["txid"] == selected_txid].iloc[0]

        dcol1, dcol2 = st.columns([1, 1])
        with dcol1:
            st.markdown(
                f"""
                <div class="alert-card alert-{str(row_data.get('risk_level', 'low')).lower()}">
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h4 style='margin:0; color:#f8fafc;'>TXID: <code>{selected_txid}</code></h4>
                        {render_risk_badge(row_data.get('risk_level', 'LOW'))}
                    </div>
                    <hr style='border-color:rgba(255,255,255,0.1); margin:10px 0;'>
                    <p style='margin:4px 0;'><b>Primary Wallet:</b> <code>{row_data.get('primary_wallet', 'N/A')}</code></p>
                    <p style='margin:4px 0;'><b>Observed Source IP:</b> <code>{row_data.get('src_ip', 'N/A')}</code> ({row_data.get('src_country', 'N/A')} - {row_data.get('src_asn', 'N/A')})</p>
                    <p style='margin:4px 0;'><b>Composite Risk Score:</b> <span style='font-size:1.1rem; font-weight:700; color:#f87171;'>{row_data.get('composite_risk_score', 0):.1f} / 100</span></p>
                    <p style='margin:4px 0;'><b>ML Probability (XGBoost):</b> {row_data.get('ml_probability', 0):.4f}</p>
                    <p style='margin:4px 0;'><b>Behavioral Anomaly Score (Isolation Forest):</b> {row_data.get('anomaly_score', 0):.1f} / 100</p>
                    <p style='margin:4px 0;'><b>Graph Neighborhood Score (GraphSAGE):</b> {row_data.get('graph_score', 0):.1f} / 100</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with dcol2:
            st.markdown("#### Neighborhood Subgraph")
            sub_G = G_forensic.subgraph(
                list(nx.single_source_shortest_path_length(G_forensic.to_undirected(), selected_txid, cutoff=2).keys())[:40]
            ) if selected_txid in G_forensic else nx.DiGraph()
            st.plotly_chart(plot_forensic_subgraph(sub_G, center_node=selected_txid), use_container_width=True)
