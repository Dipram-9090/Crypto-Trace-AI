"""
Missing Value Imputation and Data Cleaning Utilities.
"""
import pandas as pd
import numpy as np


def impute_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Impute numerical and categorical columns with robust defaults."""
    df_clean = df.copy()
    for col in df_clean.columns:
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        else:
            df_clean[col] = df_clean[col].fillna("Unknown")
    return df_clean
