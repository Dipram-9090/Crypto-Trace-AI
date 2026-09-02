"""
Temporal Correlation between P2P network broadcast and block confirmations.
"""
from typing import Dict, Any, Optional
from datetime import datetime


class TemporalCorrelator:
    """Calculates temporal broadcast anomalies, velocity bursts, and propagation delays."""
    def __init__(self):
        self.last_seen_times = {}

    def compute_broadcast_gap(self, entity_id: str, current_timestamp: str) -> float:
        try:
            cur_dt = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S")
        except Exception:
            cur_dt = datetime.now()

        last_dt = self.last_seen_times.get(entity_id)
        self.last_seen_times[entity_id] = cur_dt

        if last_dt is None:
            return 86400.0
        return max(0.0, (cur_dt - last_dt).total_seconds())
