"""
Data cleaning and validation module.
"""

import pandas as pd
import numpy as np


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, deduplicate, and enforce data types on ingested canonical transactions."""
    if df.empty:
        return df

    df = df.copy()
    df = df.drop_duplicates(subset=["txid"]).reset_index(drop=True)

    df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    df["fee"] = pd.to_numeric(df["fee"], errors="coerce").fillna(0.0)
    df["src_port"] = pd.to_numeric(df.get("src_port", 0), errors="coerce").fillna(0).astype(int)
    df["dst_port"] = pd.to_numeric(df.get("dst_port", 8333), errors="coerce").fillna(8333).astype(int)
    df["label"] = pd.to_numeric(df.get("label", 2), errors="coerce").fillna(2).astype(int)

    return df
