"""
Table rendering and metric badge helpers.
"""
import streamlit as st


def render_metric_card(title: str, value: str, subtext: str = ""):
    """Glassmorphism KPI card."""
    sub_html = f"<div style='font-size:0.75rem; color:#64748b; margin-top:2px;'>{subtext}</div>" if subtext else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_badge(risk_level: str) -> str:
    """HTML tag with risk color styling."""
    lvl = risk_level.upper()
    if lvl == "CRITICAL":
        return f'<span class="badge-critical">CRITICAL</span>'
    elif lvl == "HIGH":
        return f'<span class="badge-high">HIGH</span>'
    elif lvl == "MEDIUM":
        return f'<span class="badge-medium">MEDIUM</span>'
    else:
        return f'<span class="badge-low">LOW</span>'
