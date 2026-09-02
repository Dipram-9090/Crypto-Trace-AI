"""
Temporal dynamics and velocity feature extractor.
"""
from collections import deque, defaultdict
from datetime import datetime
from typing import Dict, Any, List


class TemporalTracker:
    """Computes rolling velocity and burst metrics for transactions and entities."""
    def __init__(self, windows_hours: List[int] = [1, 6, 24, 168], burst_threshold_sec: int = 60):
        self.windows_hours = windows_hours
        self.burst_threshold_sec = burst_threshold_sec
        self.wallet_history = defaultdict(deque)
        self.ip_history = defaultdict(deque)
        self.last_wallet_time = {}
        self.last_ip_time = {}

    def extract_and_update(self, row: Dict[str, Any]) -> Dict[str, float]:
        ts = row.get("datetime")
        if isinstance(ts, str):
            ts = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        elif not isinstance(ts, datetime):
            ts = datetime.now()

        inputs = row.get("input_addresses", [])
        primary_wallet = inputs[0] if inputs else "UNKNOWN"
        src_ip = str(row.get("src_ip", ""))

        max_sec = max(self.windows_hours) * 3600
        cutoff = ts.timestamp() - max_sec

        w_dq = self.wallet_history[primary_wallet]
        while w_dq and w_dq[0] < cutoff:
            w_dq.popleft()

        ip_dq = self.ip_history[src_ip]
        while ip_dq and ip_dq[0] < cutoff:
            ip_dq.popleft()

        last_w_t = self.last_wallet_time.get(primary_wallet)
        time_since_prev_w = max(0.0, (ts - last_w_t).total_seconds()) if last_w_t else 86400.0

        last_ip_t = self.last_ip_time.get(src_ip)
        time_since_prev_ip = max(0.0, (ts - last_ip_t).total_seconds()) if last_ip_t else 86400.0

        burst_score = 1.0 if time_since_prev_w < self.burst_threshold_sec else float(self.burst_threshold_sec / (time_since_prev_w + 1e-5))

        cur_epoch = ts.timestamp()
        w_1h = sum(1 for t in w_dq if cur_epoch - t <= 3600)
        w_6h = sum(1 for t in w_dq if cur_epoch - t <= 21600)
        w_24h = sum(1 for t in w_dq if cur_epoch - t <= 86400)
        w_7d = len(w_dq)

        ip_1h = sum(1 for t in ip_dq if cur_epoch - t <= 3600)
        ip_24h = sum(1 for t in ip_dq if cur_epoch - t <= 86400)

        w_dq.append(cur_epoch)
        ip_dq.append(cur_epoch)
        self.last_wallet_time[primary_wallet] = ts
        self.last_ip_time[src_ip] = ts

        tx_velocity = w_24h / 24.0

        return {
            "time_since_prev_wallet_tx": time_since_prev_w,
            "time_since_prev_ip_tx": time_since_prev_ip,
            "burst_score": burst_score,
            "wallet_txs_last_1h": float(w_1h),
            "wallet_txs_last_6h": float(w_6h),
            "wallet_txs_last_24h": float(w_24h),
            "wallet_txs_last_7d": float(w_7d),
            "ip_txs_last_1h": float(ip_1h),
            "ip_txs_last_24h": float(ip_24h),
            "wallet_tx_velocity_per_hour": tx_velocity
        }
