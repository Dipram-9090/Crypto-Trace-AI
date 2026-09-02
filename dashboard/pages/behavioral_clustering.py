"""
Behavioral Clustering & Dimensionality Reduction Dashboard Page.
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.cryptotrace.models.clustering import BehavioralClusterer


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 🔬 Unsupervised Behavioral Clustering & PCA")
    st.markdown("Discover latent behavioral archetypes (e.g., rapid mixing rings, peeling chains, exchange hot wallets) without human labeling bias.")

    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type", "ml_probability", "anomaly_score", "graph_score", "composite_risk_score", "risk_level"]
    feature_cols = [c for c in df_scored.columns if c not in meta_cols]

    if not feature_cols:
        st.info("Insufficient features for clustering.")
        return

    X = df_scored[feature_cols].fillna(0.0)

    clusterer_path = "models/clustering/behavioral_clusterer.pkl"
    if os.path.exists(clusterer_path):
        clusterer = BehavioralClusterer.load(clusterer_path)
        labels, coords_2d = clusterer.fit_predict(X)
    else:
        clusterer = BehavioralClusterer(eps=1.5, min_samples=5)
        labels, coords_2d = clusterer.fit_predict(X)

    plot_df = pd.DataFrame({
        "txid": df_scored["txid"],
        "PCA_Dim1": coords_2d[:, 0],
        "PCA_Dim2": coords_2d[:, 1],
        "Cluster": [f"Cluster {l}" if l != -1 else "Outlier / Noise" for l in labels],
        "Risk_Score": df_scored.get("composite_risk_score", 0),
        "Archetype": df_scored.get("entity_type", "Unknown"),
        "Wallet": df_scored.get("primary_wallet", "N/A"),
        "FanOut": df_scored.get("fan_out_ratio", 1.0)
    })

    ccol1, ccol2 = st.columns([2, 1])
    with ccol1:
        fig_pca = px.scatter(
            plot_df,
            x="PCA_Dim1",
            y="PCA_Dim2",
            color="Cluster",
            hover_data=["txid", "Wallet", "Archetype", "Risk_Score", "FanOut"],
            title="2D PCA Dimensionality Projection of Behavioral Clusters"
        )
        fig_pca.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"), height=480)
        st.plotly_chart(fig_pca, use_container_width=True)

    with ccol2:
        st.markdown("#### Discovered Cluster Archetypes")
        summary_df = clusterer.summarize_clusters(df_scored, labels)
        st.dataframe(summary_df, use_container_width=True, height=450)
