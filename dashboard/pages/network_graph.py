"""
Heterogeneous Forensic Network Graph Page.
"""
import streamlit as st
import pandas as pd
import networkx as nx
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.graph.analytics import GraphAnalytics
from dashboard.components.graph_view import plot_forensic_subgraph


def render_page(df_scored: pd.DataFrame, G_forensic: nx.DiGraph):
    st.markdown("## 🕸️ Heterogeneous Forensic Network Graph")
    st.markdown("Multi-relational graph topology correlating Wallets, Transactions, Observed IPs, ASNs, and Geographic Locations.")

    gcol1, gcol2 = st.columns([1, 3])
    with gcol1:
        target_entity = st.text_input("Center Node ID (Wallet, TX, or IP)", value=list(df_scored["txid"])[0] if not df_scored.empty else "")
        hop_distance = st.slider("Neighborhood Hop Distance", min_value=1, max_value=3, value=2)
        max_nodes = st.slider("Max Display Nodes", min_value=20, max_value=150, value=60)

    with gcol2:
        analytics = GraphAnalytics(G_forensic)
        sub_G = analytics.extract_subgraph(target_entity, hops=hop_distance, max_nodes=max_nodes)
        
        st.markdown(f"**Subgraph View:** {sub_G.number_of_nodes()} nodes, {sub_G.number_of_edges()} edges centered on `{target_entity}`")
        st.plotly_chart(plot_forensic_subgraph(sub_G, center_node=target_entity), use_container_width=True)
