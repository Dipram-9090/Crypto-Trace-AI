"""Transaction Cleaner and Schema Standardizer."""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger("cryptotrace.ai_ml.preprocessing")


class TransactionCleaner:
    """Cleans and standardizes raw blockchain transactions into analytical schemas."""

    def __init__(self, fill_strategy: str = "median", clip_outliers: bool = True):
        self.fill_strategy = fill_strategy
        self.clip_outliers = clip_outliers
        self.required_columns = ["tx_hash", "amount", "timestamp", "sender", "receiver"]

    def clean_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitizes raw records, removes duplicates, handles NaNs, and standardizes types."""
        cleaned = df.copy()

        # Handle duplicates
        if "tx_hash" in cleaned.columns:
            cleaned = cleaned.drop_duplicates(subset=["tx_hash"])

        # Datetime standardization
        if "timestamp" in cleaned.columns:
            cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="coerce")
            cleaned["timestamp"] = cleaned["timestamp"].fillna(pd.Timestamp.now())

        # Numeric sanitization
        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.fill_strategy == "median":
                cleaned[col] = cleaned[col].fillna(cleaned[col].median() if not cleaned[col].empty else 0.0)
            elif self.fill_strategy == "mean":
                cleaned[col] = cleaned[col].fillna(cleaned[col].mean() if not cleaned[col].empty else 0.0)
            else:
                cleaned[col] = cleaned[col].fillna(0.0)

            # Cap extreme anomalies if required
            if self.clip_outliers and len(cleaned) > 20:
                p99 = cleaned[col].quantile(0.999)
                p01 = cleaned[col].quantile(0.001)
                cleaned[col] = cleaned[col].clip(lower=p01, upper=p99)

        # Categorical strings
        str_cols = ["sender", "receiver", "currency", "chain", "tx_hash"]
        for col in str_cols:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].astype(str).str.strip().str.lower()

        logger.info(f"Cleaned {len(cleaned)} transaction records successfully.")
        return cleaned

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validates that all essential columns exist."""
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            logger.warning(f"Missing required columns in dataset: {missing}")
            return False
        return True
