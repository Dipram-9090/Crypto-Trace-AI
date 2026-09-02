"""
Forensic Alert Card UI Component.
"""
import streamlit as st
from dashboard.components.tables import render_risk_badge


def render_alert_card(alert_data: dict):
    """Renders formatted glassmorphism investigative alert card."""
    risk_level = alert_data.get("risk_level", "LOW")
    st.markdown(
        f"""
        <div class="alert-card alert-{risk_level.lower()}">
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <h4 style='margin:0; color:#f8fafc;'>Alert <code>{alert_data.get('alert_id', 'N/A')}</code>: TXID <code>{alert_data.get('txid', 'N/A')}</code></h4>
                {render_risk_badge(risk_level)}
            </div>
            <p style='margin:6px 0;'><b>Primary Wallet:</b> <code>{alert_data.get('primary_wallet', 'N/A')}</code></p>
            <p style='margin:6px 0;'><b>Observed Endpoint:</b> <code>{alert_data.get('src_ip', 'N/A')}</code> ({alert_data.get('src_country', 'N/A')} - {alert_data.get('src_asn', 'N/A')})</p>
            <p style='margin:6px 0;'><b>Composite Risk Score:</b> <span style='font-size:1.1rem; font-weight:700; color:#f87171;'>{alert_data.get('risk_score', 0):.1f} / 100</span> (Confidence: {alert_data.get('confidence', 0.85)*100:.0f}%)</p>
        </div>
        """,
        unsafe_allow_html=True
    )
