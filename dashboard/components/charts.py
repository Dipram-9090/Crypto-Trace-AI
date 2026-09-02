"""
Plotly chart components for the dashboard.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


def plot_risk_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """Pie chart showing distribution across risk tiers."""
    counts = df["risk_level"].value_counts().reset_index()
    counts.columns = ["Risk Tier", "Count"]
    color_map = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#eab308",
        "LOW": "#22c55e"
    }
    fig = px.pie(
        counts,
        names="Risk Tier",
        values="Count",
        hole=0.45,
        color="Risk Tier",
        color_discrete_map=color_map,
        title="Transaction Breakdown by Risk Tier"
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"))
    return fig


def plot_shap_waterfall(evidence_items: List[Dict[str, Any]], title: str = "SHAP Decision Impact") -> go.Figure:
    """Waterfall/horizontal bar chart of SHAP feature contributions."""
    if not evidence_items:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark")
        return fig

    df_ev = pd.DataFrame(evidence_items).sort_values("magnitude", ascending=True)
    colors = ['#ef4444' if d == 'increased_risk' else '#10b981' for d in df_ev['direction']]

    fig = go.Figure(go.Bar(
        x=df_ev['shap_value'],
        y=df_ev['description'],
        orientation='h',
        marker=dict(color=colors, line=dict(width=1, color='rgba(255,255,255,0.2)')),
        text=[f"Val: {v}" for v in df_ev['value']],
        textposition='auto',
        hoverinfo='text+x'
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#f8fafc")),
        xaxis=dict(title="SHAP Impact (+ Increases Risk, - Decreases Risk)", zeroline=True, zerolinecolor="#64748b"),
        yaxis=dict(title=""),
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(15, 23, 42, 0.4)',
        margin=dict(l=10, r=10, t=40, b=30),
        height=320,
        font=dict(color="#cbd5e1")
    )
    return fig
