"""
Network Timing, Latency, and Broadcast Delta Analyzer.
"""

from datetime import datetime
from typing import Optional


def compute_time_delta_seconds(t1: str, t2: str) -> float:
    """Compute absolute difference in seconds between two ISO timestamp strings."""
    try:
        dt1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
        return abs((dt1 - dt2).total_seconds())
    except Exception:
        return 86400.0
