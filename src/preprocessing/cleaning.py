"""
Data cleaning and validation module for CryptoTrace AI.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, deduplicate, and enforce data types on ingested canonical transactions.
    """
    if df.empty:
        return df

    df = df.copy()

    # Drop duplicate txids
    df = df.drop_duplicates(subset=["txid"]).reset_index(drop=True)

    # Convert timestamp
    df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    # Clean numeric fields
    df["fee"] = pd.to_numeric(df["fee"], errors="coerce").fillna(0.0)
    df["src_port"] = pd.to_numeric(df["src_port"], errors="coerce").fillna(0).astype(int)
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(8333).astype(int)
    df["label"] = pd.to_numeric(df["label"], errors="coerce").fillna(2).astype(int)

    # String sanitization
    for col in ["src_ip", "dst_ip", "script_type", "src_country", "dst_country", "src_asn", "dst_asn", "entity_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df
