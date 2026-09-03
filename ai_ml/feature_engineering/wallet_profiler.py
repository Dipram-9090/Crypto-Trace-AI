"""Wallet Behavioral Profiler and Heuristics Extractor."""

from typing import Dict, Any
import pandas as pd
import numpy as np


class WalletFeatureProfiler:
    """Profiles wallet transaction patterns: peeling chains, structuring/smurfing, and address reuse."""

    @staticmethod
    def profile_wallets(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates sender and receiver transaction patterns into wallet risk metrics."""
        if df.empty:
            return pd.DataFrame()

        # Sender statistics
        sent = df.groupby("sender").agg(
            total_sent_amount=("amount", "sum"),
            avg_sent_amount=("amount", "mean"),
            std_sent_amount=("amount", "std"),
            max_sent_amount=("amount", "max"),
            tx_count_out=("tx_hash", "count"),
            unique_recipients=("receiver", "nunique")
        ).reset_index().rename(columns={"sender": "address"})

        # Receiver statistics
        rcvd = df.groupby("receiver").agg(
            total_rcvd_amount=("amount", "sum"),
            avg_rcvd_amount=("amount", "mean"),
            std_rcvd_amount=("amount", "std"),
            max_rcvd_amount=("amount", "max"),
            tx_count_in=("tx_hash", "count"),
            unique_senders=("sender", "nunique")
        ).reset_index().rename(columns={"receiver": "address"})

        # Merge
        profile = pd.merge(sent, rcvd, on="address", how="outer").fillna(0)
        profile["total_txs"] = profile["tx_count_out"] + profile["tx_count_in"]
        profile["net_flow"] = profile["total_rcvd_amount"] - profile["total_sent_amount"]
        profile["turnover_ratio"] = profile["total_sent_amount"] / (profile["total_rcvd_amount"] + 1e-5)
        
        # Peeling / Mixing Indicators
        # A wallet with high turnover and high fan-out with small standard deviation indicates automated splitting
        profile["peeling_indicator"] = (
            (profile["tx_count_out"] > 5) & 
            (profile["unique_recipients"] / (profile["tx_count_out"] + 1e-5) > 0.8) &
            (profile["turnover_ratio"] > 0.85)
        ).astype(int)

        return profile
