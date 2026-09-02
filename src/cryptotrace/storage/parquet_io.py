"""
High-performance Parquet storage reader and writer for CryptoTrace AI.
"""

import os
import pandas as pd
from typing import Optional
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def write_parquet(df: pd.DataFrame, filepath: str, compression: str = "snappy") -> str:
    """Serialize dataframe to columnar compressed Parquet format."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath, compression=compression, index=False)
    logger.info(f"Saved {len(df):,} records to Parquet: {filepath}")
    return filepath


def read_parquet(filepath: str, columns: Optional[list] = None) -> pd.DataFrame:
    """Read dataframe from Parquet format with optional column projection."""
    if not os.path.exists(filepath):
        logger.warning(f"Parquet file does not exist: {filepath}")
        return pd.DataFrame()
    return pd.read_parquet(filepath, columns=columns)
