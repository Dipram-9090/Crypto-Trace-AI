"""
Network Telemetry Synthesizer & Public Dataset Bridge.
Enriches public blockchain datasets (Elliptic, Elliptic++, BitcoinHeist) with realistic P2P network-layer observations.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.cryptotrace.geoip.lookup import GeoIPLookup
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)

IP_POOLS = {
    "suspicious": ["185.220.101.5", "185.220.101.9", "45.154.255.88", "198.51.100.24", "91.240.118.50"],
    "exchange": ["51.15.89.2", "104.244.72.115", "104.244.72.116", "178.62.204.10", "119.81.100.40"],
    "miner": ["103.21.244.2", "103.21.244.5", "51.15.89.100"],
    "normal": ["104.244.72.1", "178.62.204.5", "103.21.244.10", "119.81.100.10", "51.15.89.50"]
}


class NetworkObservationBridge:
    """Bridges transaction IDs with realistic P2P network transmission events."""
    def __init__(self, geoip: Optional[GeoIPLookup] = None):
        self.geoip = geoip or GeoIPLookup()

    def bridge_elliptic_dataset(self, elliptic_df: pd.DataFrame, base_time: Optional[datetime] = None) -> pd.DataFrame:
        """Adds src_ip, dst_ip, ports, timestamps, ASN, and country to Elliptic transaction records."""
        base_t = base_time or datetime(2026, 1, 1, 8, 0, 0)
        enriched_rows = []

        for idx, row in elliptic_df.iterrows():
            txid = str(row.get("txId", f"TX_{idx:06d}"))
            timestep = int(row.get("time_step", 1))
            label = int(row.get("label", 2))

            # Map time step to timestamp
            tx_time = base_t + timedelta(hours=timestep * 2, minutes=int(idx % 120))

            if label == 1:
                # Illicit / suspicious transaction
                src_ip = np.random.choice(IP_POOLS["suspicious"])
                src_port = np.random.randint(40000, 65000)
                entity_archetype = "SUSPICIOUS_ACTOR"
            elif label == 0:
                # Licit transaction
                pool_choice = np.random.choice(["normal", "exchange", "miner"], p=[0.70, 0.20, 0.10])
                src_ip = np.random.choice(IP_POOLS[pool_choice])
                src_port = np.random.randint(1025, 40000)
                entity_archetype = pool_choice.upper()
            else:
                src_ip = np.random.choice(IP_POOLS["normal"])
                src_port = np.random.randint(1025, 60000)
                entity_archetype = "UNKNOWN"

            dst_ip = "51.15.89.2"
            dst_port = 8333

            geo_info = self.geoip.lookup(src_ip)

            rec = row.to_dict()
            rec.update({
                "txid": txid,
                "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                "datetime": tx_time,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "src_country": geo_info.country,
                "src_asn": geo_info.asn,
                "entity_type": entity_archetype
            })
            enriched_rows.append(rec)

        return pd.DataFrame(enriched_rows)
