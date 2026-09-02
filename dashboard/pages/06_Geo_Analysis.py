"""
Geographic & ASN Analysis Page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 🌍 Geographic & ASN Infrastructure Intelligence")
    st.markdown("Spatial distribution and Autonomous System concentrations of observed Bitcoin network traffic.")

    if "src_country" in df_scored.columns:
        geo_counts = df_scored["src_country"].value_counts().reset_index()
        geo_counts.columns = ["Country", "Transactions"]

        fig_geo = px.choropleth(
            geo_counts,
            locations="Country",
            locationmode="country names",
            color="Transactions",
            color_continuous_scale="Viridis",
            title="Observed Transaction Ingestion Density by Country"
        )
        fig_geo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"))
        st.plotly_chart(fig_geo, use_container_width=True)

    if "src_asn" in df_scored.columns:
        asn_counts = df_scored["src_asn"].value_counts().head(10).reset_index()
        asn_counts.columns = ["Autonomous System (ASN)", "Count"]
        fig_asn = px.bar(
            asn_counts,
            x="Autonomous System (ASN)",
            y="Count",
            title="Top 10 Autonomous Systems (ASNs) Hosting Observed Transaction Traffic"
        )
        fig_asn.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"))
        st.plotly_chart(fig_asn, use_container_width=True)
