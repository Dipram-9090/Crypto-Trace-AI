"""Temporal and Velocity Feature Engineering."""

import pandas as pd
import numpy as np


class TemporalFeatureExtractor:
    """Extracts burstiness, time-since-last-tx, inter-arrival time stats, and cyclical clock features."""

    @staticmethod
    def extract_temporal_features(df: pd.DataFrame, time_col: str = "timestamp", entity_col: str = "sender") -> pd.DataFrame:
        """Extracts cyclical hour/day features and entity-level temporal burstiness."""
        data = df.copy()
        if time_col not in data.columns:
            return data

        data[time_col] = pd.to_datetime(data[time_col])

        # Cyclical clock encodings
        hours = data[time_col].dt.hour
        days = data[time_col].dt.dayofweek

        data["hour_sin"] = np.sin(2 * np.pi * hours / 24.0)
        data["hour_cos"] = np.cos(2 * np.pi * hours / 24.0)
        data["day_sin"] = np.sin(2 * np.pi * days / 7.0)
        data["day_cos"] = np.cos(2 * np.pi * days / 7.0)
        data["is_weekend"] = days.isin([5, 6]).astype(int)

        # Entity velocity (burst transactions within short time intervals)
        if entity_col in data.columns:
            data = data.sort_values(by=[entity_col, time_col])
            data["time_diff_secs"] = data.groupby(entity_col)[time_col].diff().dt.total_seconds().fillna(86400)
            data["tx_velocity_1h"] = data.groupby(entity_col)[time_col].transform(
                lambda s: s.rolling("1h", on=s).count() if len(s) > 1 else 1
            ).fillna(1)
        else:
            data["time_diff_secs"] = 86400
            data["tx_velocity_1h"] = 1

        return data
