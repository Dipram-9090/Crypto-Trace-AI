"""
DuckDB Analytical Querying & Parquet Explorer Page.
"""
import streamlit as st
import pandas as pd
from src.cryptotrace.storage.duckdb_engine import DuckDBQueryEngine


def render_page(df_scored: pd.DataFrame):
    st.markdown("## 🦆 High-Performance DuckDB Analytics")
    st.markdown("Execute in-memory SQL analytical queries directly on Parquet and memory dataframes.")

    engine = DuckDBQueryEngine()
    engine.register_dataframe("transactions", df_scored)

    tab1, tab2, tab3 = st.tabs(["📊 Wallet Aggregates", "🌐 IP Infrastructure Intelligence", "💻 Interactive SQL Console"])

    with tab1:
        st.markdown("### Top Aggregated Wallets by Volume & Risk")
        w_df = engine.get_wallet_summary("transactions")
        st.dataframe(w_df.head(50), use_container_width=True, height=400)

    with tab2:
        st.markdown("### IP Address Colocation & Network Concentration")
        ip_df = engine.get_ip_infrastructure_summary("transactions")
        st.dataframe(ip_df.head(50), use_container_width=True, height=400)

    with tab3:
        st.markdown("### Custom Analytical SQL Query")
        default_query = """
        SELECT 
            entity_type,
            COUNT(*) as tx_count,
            ROUND(AVG(composite_risk_score), 1) as avg_risk,
            ROUND(AVG(fan_out_ratio), 2) as avg_fanout,
            ROUND(SUM(transaction_value), 2) as total_btc
        FROM transactions
        GROUP BY entity_type
        ORDER BY avg_risk DESC;
        """
        user_sql = st.text_area("SQL Statement (Table: `transactions`)", value=default_query.strip(), height=130)
        if st.button("Run SQL Query", type="primary"):
            custom_res = engine.query(user_sql)
            st.dataframe(custom_res, use_container_width=True)
