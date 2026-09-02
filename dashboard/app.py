"""
CryptoTrace AI - Main Forensic Analytics Dashboard.
"""
import os
import sys
import streamlit as st
import pandas as pd
import networkx as nx

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.storage.parquet_io import read_parquet
from dashboard.pages import (
    overview,
    alert_triage,
    transaction_explorer,
    wallet_forensics,
    network_graph,
    geo_analysis,
    shap_explainability,
    model_benchmarks,
    behavioral_clustering,
    duckdb_analytics
)

st.set_page_config(
    page_title="CryptoTrace AI | Forensic Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_dashboard_data():
    scored_parquet = "reports/scored_transactions.parquet"
    scored_csv = "reports/scored_transactions.csv"
    features_parquet = "data/processed/features.parquet"
    features_csv = "data/processed/features.csv"
    synthetic_parquet = "data/synthetic/transactions.parquet"
    synthetic_csv = "data/synthetic/transactions.csv"
    comparison_csv = "reports/metrics/model_comparison.csv"
    if not os.path.exists(comparison_csv):
        comparison_csv = "reports/model_comparison.csv"

    if os.path.exists(scored_parquet):
        df_scored = read_parquet(scored_parquet)
    elif os.path.exists(scored_csv):
        df_scored = pd.read_csv(scored_csv)
    elif os.path.exists(features_parquet):
        df_scored = read_parquet(features_parquet)
    elif os.path.exists(features_csv):
        df_scored = pd.read_csv(features_csv)
    elif os.path.exists(synthetic_parquet):
        df_scored = read_parquet(synthetic_parquet)
    elif os.path.exists(synthetic_csv):
        df_scored = pd.read_csv(synthetic_csv)
    else:
        df_scored = pd.DataFrame()

    comp_df = pd.read_csv(comparison_csv) if os.path.exists(comparison_csv) else pd.DataFrame()
    return df_scored, comp_df


@st.cache_resource
def get_graph(df: pd.DataFrame):
    builder = ForensicGraphBuilder()
    return builder.build_from_dataframe(df)


df_scored, comparison_df = load_dashboard_data()
G_forensic = get_graph(df_scored) if not df_scored.empty else nx.DiGraph()

# Sidebar
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 10px 0;'>
        <h2 style='color: #60a5fa; margin-bottom: 0;'>🛡️ CryptoTrace AI</h2>
        <p style='color: #94a3b8; font-size: 0.8rem;'>Forensic Graph & ML Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)

pages = {
    "Overview": lambda: overview.render_page(df_scored),
    "Alert Ranking & Triage": lambda: alert_triage.render_page(df_scored, G_forensic),
    "Transaction Explorer": lambda: transaction_explorer.render_page(df_scored),
    "Wallet Forensics": lambda: wallet_forensics.render_page(df_scored),
    "Network Graph": lambda: network_graph.render_page(df_scored, G_forensic),
    "Geographic & ASN Analysis": lambda: geo_analysis.render_page(df_scored),
    "Behavioral Clustering & PCA": lambda: behavioral_clustering.render_page(df_scored),
    "DuckDB SQL Analytics": lambda: duckdb_analytics.render_page(df_scored),
    "Model Explainability (SHAP)": lambda: shap_explainability.render_page(df_scored),
    "Model Performance & Benchmarks": lambda: model_benchmarks.render_page(comparison_df)
}

selected = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='font-size:0.75rem; color:#64748b; line-height: 1.4;'>
        <b>Forensic Notice:</b><br>
        Network & GeoIP correlations provide contextual investigative leads and do not constitute proof of individual identity.
    </div>
    """,
    unsafe_allow_html=True
)

if df_scored.empty:
    st.warning("⚠️ No dataset loaded. Please run data preparation and training first.")
else:
    pages[selected]()
