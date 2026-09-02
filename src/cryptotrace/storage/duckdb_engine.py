"""
DuckDB Analytical Query Engine for Forensic Transactions and Parquet data.
"""
import os
from typing import Optional, Dict, Any, List
import pandas as pd
try:
    import duckdb
except ImportError:
    duckdb = None

from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class DuckDBQueryEngine:
    """Embedded columnar analytical query engine for fast entity aggregations and forensic queries."""
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path) if duckdb is not None else None

    def register_dataframe(self, name: str, df: pd.DataFrame):
        """Register a pandas DataFrame as a virtual table in DuckDB."""
        if self.conn is not None:
            self.conn.register(name, df)

    def register_parquet(self, name: str, parquet_path: str):
        """Register Parquet file as a view in DuckDB."""
        if self.conn is not None and os.path.exists(parquet_path):
            self.conn.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{parquet_path}')")

    def query(self, sql: str) -> pd.DataFrame:
        """Execute analytical SQL query and return results as pandas DataFrame."""
        if self.conn is None:
            logger.warning("DuckDB is not installed, returning empty dataframe.")
            return pd.DataFrame()
        try:
            return self.conn.execute(sql).df()
        except Exception as e:
            logger.error(f"DuckDB Query Error: {e}")
            return pd.DataFrame()

    def get_wallet_summary(self, table_name: str = "transactions") -> pd.DataFrame:
        """Analytical query aggregating total volume, distinct counterparties, and peak fees per wallet."""
        sql = f"""
        SELECT 
            primary_wallet,
            COUNT(txid) as total_tx_count,
            SUM(transaction_value) as total_volume_btc,
            AVG(transaction_value) as avg_tx_value,
            MAX(transaction_value) as max_tx_value,
            SUM(fee) as total_fees_paid,
            COUNT(DISTINCT src_ip) as distinct_ips,
            COUNT(DISTINCT src_country) as distinct_countries,
            MAX(composite_risk_score) as max_risk_score
        FROM {table_name}
        WHERE primary_wallet IS NOT NULL AND primary_wallet != ''
        GROUP BY primary_wallet
        ORDER BY total_tx_count DESC
        """
        return self.query(sql)

    def get_ip_infrastructure_summary(self, table_name: str = "transactions") -> pd.DataFrame:
        """Analytical query mapping IP addresses to associated wallets and ASN concentrations."""
        sql = f"""
        SELECT 
            src_ip,
            src_country,
            src_asn,
            COUNT(txid) as tx_count,
            COUNT(DISTINCT primary_wallet) as associated_wallets,
            SUM(transaction_value) as total_btc_transacted,
            AVG(composite_risk_score) as avg_risk_score
        FROM {table_name}
        WHERE src_ip IS NOT NULL AND src_ip != ''
        GROUP BY src_ip, src_country, src_asn
        ORDER BY associated_wallets DESC, tx_count DESC
        """
        return self.query(sql)
