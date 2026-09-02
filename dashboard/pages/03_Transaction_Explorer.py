"""
Detailed Transaction Explorer Page.
"""
import streamlit as st
import pandas as pd


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 🔎 Detailed Transaction Explorer")
    st.markdown("Examine atomic blockchain transaction structures and network transmission properties.")

    tx_list = list(df_scored["txid"].dropna().head(100))
    selected_tx = st.selectbox("Choose Transaction ID", tx_list)
    tx_row = df_scored[df_scored["txid"] == selected_tx].iloc[0]

    ecol1, ecol2, ecol3 = st.columns(3)
    with ecol1:
        st.markdown("#### Blockchain Structure")
        st.write(f"**Transaction Value:** {tx_row.get('transaction_value', 0.0):.4f} BTC")
        st.write(f"**Miner Fee:** {tx_row.get('fee', 0.0):.6f} BTC")
        st.write(f"**Input Count:** {tx_row.get('input_count', 1)}")
        st.write(f"**Output Count:** {tx_row.get('output_count', 1)}")
        st.write(f"**Fan-out Ratio:** {tx_row.get('fan_out_ratio', 1.0):.2f}")
    with ecol2:
        st.markdown("#### Network Layer Metadata")
        st.write(f"**Source IP:** `{tx_row.get('src_ip', 'N/A')}`")
        st.write(f"**Destination IP:** `{tx_row.get('dst_ip', 'N/A')}`")
        st.write(f"**Ports:** {tx_row.get('src_port', 0)} → {tx_row.get('dst_port', 8333)}")
        st.write(f"**Country:** {tx_row.get('src_country', 'N/A')}")
        st.write(f"**ASN:** {tx_row.get('src_asn', 'N/A')}")
    with ecol3:
        st.markdown("#### Temporal & Behavioral Dynamics")
        st.write(f"**Timestamp:** {tx_row.get('timestamp', 'N/A')}")
        st.write(f"**Burst Score:** {tx_row.get('burst_score', 0.0):.2f}")
        st.write(f"**Velocity (TXs/24h):** {tx_row.get('wallet_txs_last_24h', 0)}")
        st.write(f"**Shared IP Index:** {tx_row.get('shared_infrastructure_indicator', 0.0):.2f}")
