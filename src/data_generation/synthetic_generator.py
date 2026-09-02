"""
Synthetic Bitcoin transaction and network-layer metadata generator.
Simulates realistic behavioral archetypes with realistic overlapping distributions.
"""

import random
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any, Tuple
import logging
from src.geoip.lookup import GeoIPLookup

logger = logging.getLogger(__name__)

ACTOR_TYPES = ["NORMAL_USER", "EXCHANGE", "MERCHANT", "MINER", "HIGH_VOLUME_SERVICE", "SUSPICIOUS_ACTOR"]

SCRIPT_TYPES = ["p2pkh", "p2sh", "p2wpkh", "p2wsh", "p2tr", "multisig"]


class SyntheticDataGenerator:
    """
    Generates multi-layer Bitcoin blockchain and network correlation data.
    """

    def __init__(
        self,
        num_transactions: int = 12000,
        num_wallets: int = 1200,
        num_ips: int = 150,
        illicit_ratio: float = 0.08,
        seed: int = 42,
    ):
        self.num_transactions = num_transactions
        self.num_wallets = num_wallets
        self.num_ips = num_ips
        self.illicit_ratio = illicit_ratio
        self.seed = seed
        self.geoip = GeoIPLookup()

        random.seed(self.seed)

        # Initialize pools
        self.wallets: List[str] = [
            f"1BTC{i:05d}{random.choice(['a', 'b', 'c', 'x', 'y', 'z'])}" for i in range(self.num_wallets)
        ]
        self.ips: List[str] = self._generate_ip_pool()
        self.entities: Dict[str, Dict[str, Any]] = self._assign_entity_profiles()

    def _generate_ip_pool(self) -> List[str]:
        """Generate a realistic pool of public IP addresses across subnets."""
        subnets = [
            "185.220.101.",  # NL / VPN / Tor exit
            "51.15.89.",  # DE / Cloud
            "104.244.72.",  # US / Hosting
            "45.33.32.",  # CH / Dedicated
            "194.87.144.",  # RU / VPS
            "103.21.244.",  # IN / Telecom
            "178.62.204.",  # GB / DigitalOcean
            "119.81.130.",  # SG / SoftLayer
            "198.51.100.",  # PA / Offshore
            "91.200.12.",  # SC / Hosting
        ]
        ips = []
        for i in range(self.num_ips):
            subnet = random.choice(subnets)
            host = random.randint(2, 254)
            ips.append(f"{subnet}{host}")
        return list(set(ips))

    def _assign_entity_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Assign wallets to behavioral entity types and dedicated infrastructure."""
        num_actors = max(50, self.num_wallets // 15)
        entities = {}

        # Distribution weights: Normal users ~50%, Merchants ~15%, Exchanges ~10%, Miners ~10%, High Volume ~8%, Suspicious ~7%
        weights = [0.50, 0.10, 0.15, 0.10, 0.08, 0.07]

        for i in range(num_actors):
            actor_id = f"ACTOR_{i:04d}"
            actor_type = random.choices(ACTOR_TYPES, weights=weights)[0]

            # Suspicious actor ratio constraint
            if actor_type == "SUSPICIOUS_ACTOR":
                label = 1
            else:
                label = 0

            # Allocate wallet cluster to actor
            if actor_type == "EXCHANGE":
                cluster_size = random.randint(15, 45)
                ip_count = random.randint(5, 12)
            elif actor_type == "SUSPICIOUS_ACTOR":
                cluster_size = random.randint(6, 25)
                ip_count = random.randint(6, 18)  # Frequent IP hopping
            elif actor_type == "HIGH_VOLUME_SERVICE":
                cluster_size = random.randint(10, 30)
                ip_count = random.randint(3, 8)
            elif actor_type == "MINER":
                cluster_size = random.randint(3, 8)
                ip_count = random.randint(1, 3)
            elif actor_type == "MERCHANT":
                cluster_size = random.randint(4, 12)
                ip_count = random.randint(2, 4)
            else:  # NORMAL_USER
                cluster_size = random.randint(1, 4)
                ip_count = random.randint(1, 2)

            actor_wallets = random.sample(self.wallets, min(cluster_size, len(self.wallets)))
            actor_ips = random.sample(self.ips, min(ip_count, len(self.ips)))

            entities[actor_id] = {
                "actor_id": actor_id,
                "actor_type": actor_type,
                "label": label,
                "wallets": actor_wallets,
                "ips": actor_ips,
            }

        return entities

    def generate_transactions(self) -> List[Dict[str, Any]]:
        """Generate canonical transaction list sorted by timestamp."""
        base_time = datetime(2026, 1, 1, 0, 0, 0)
        transactions = []
        entity_list = list(self.entities.values())

        # Generate sequential timeline
        current_time = base_time

        for i in range(self.num_transactions):
            # Select entity according to realistic activity volume
            actor = random.choice(entity_list)
            actor_type = actor["actor_type"]

            # Time advancement
            if actor_type == "SUSPICIOUS_ACTOR" and random.random() < 0.65:
                # Burst behavior: very close intervals (1 to 20 seconds)
                time_delta = timedelta(seconds=random.randint(1, 20))
            elif actor_type in ["EXCHANGE", "HIGH_VOLUME_SERVICE"]:
                time_delta = timedelta(seconds=random.randint(5, 60))
            else:
                time_delta = timedelta(seconds=random.randint(30, 900))

            current_time += time_delta

            txid = f"TX_{i+1:06d}_{hash(str(current_time) + str(i)) % 10000:04d}"

            # Select source and destination IPs
            src_ip = random.choice(actor["ips"])
            dst_ip = random.choice(self.ips)
            src_port = random.randint(1024, 65535) if actor_type != "MINER" else 8333
            dst_port = 8333 if random.random() < 0.85 else random.randint(1024, 65535)

            # Generate inputs, outputs, amounts
            if actor_type == "SUSPICIOUS_ACTOR":
                # Layering / Peeling / Fan-out behavior
                if random.random() < 0.5:
                    # High fan-out
                    num_inputs = random.randint(1, 2)
                    num_outputs = random.randint(8, 25)
                else:
                    # Rapid peeling / consolidation
                    num_inputs = random.randint(4, 12)
                    num_outputs = random.randint(1, 3)
                base_amount = random.uniform(0.5, 45.0)
            elif actor_type == "EXCHANGE":
                # High fan-in and fan-out (legitimate high volume overlap)
                num_inputs = random.randint(3, 15)
                num_outputs = random.randint(4, 20)
                base_amount = random.uniform(5.0, 150.0)
            elif actor_type == "MINER":
                num_inputs = 1
                num_outputs = random.randint(1, 5)
                base_amount = random.uniform(3.125, 12.5)
            elif actor_type == "MERCHANT":
                num_inputs = random.randint(1, 4)
                num_outputs = random.randint(1, 3)
                base_amount = random.uniform(0.01, 2.5)
            elif actor_type == "HIGH_VOLUME_SERVICE":
                num_inputs = random.randint(2, 6)
                num_outputs = random.randint(2, 8)
                base_amount = random.uniform(0.1, 10.0)
            else:  # NORMAL_USER
                num_inputs = random.randint(1, 2)
                num_outputs = random.randint(1, 2)
                base_amount = random.uniform(0.005, 1.8)

            inputs = random.sample(actor["wallets"], min(num_inputs, len(actor["wallets"])))
            if len(inputs) < num_inputs:
                inputs += [random.choice(self.wallets) for _ in range(num_inputs - len(inputs))]

            outputs = random.sample(self.wallets, min(num_outputs, len(self.wallets)))

            # Input amounts
            in_slice = base_amount / len(inputs)
            input_amounts = [
                round(max(0.0001, in_slice + random.uniform(-in_slice * 0.1, in_slice * 0.1)), 6) for _ in inputs
            ]
            total_in = sum(input_amounts)

            fee = round(max(0.00005, total_in * random.uniform(0.0001, 0.002)), 6)
            total_out = total_in - fee

            out_slice = total_out / len(outputs)
            output_amounts = [
                round(max(0.0001, out_slice + random.uniform(-out_slice * 0.15, out_slice * 0.15)), 6) for _ in outputs
            ]
            # Balance last output exactly
            output_amounts[-1] = round(max(0.0001, total_out - sum(output_amounts[:-1])), 6)

            # GeoIP enrichment
            src_geo = self.geoip.lookup(src_ip)
            dst_geo = self.geoip.lookup(dst_ip)

            rec = {
                "txid": txid,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "input_addresses": inputs,
                "output_addresses": outputs,
                "input_amounts": input_amounts,
                "output_amounts": output_amounts,
                "fee": fee,
                "script_type": random.choice(SCRIPT_TYPES),
                "src_country": src_geo.country,
                "dst_country": dst_geo.country,
                "src_asn": src_geo.asn,
                "dst_asn": dst_geo.asn,
                "label": actor["label"],
                "entity_type": actor_type,
            }
            transactions.append(rec)

        # Sort chronologically to preserve temporal reality
        transactions.sort(key=lambda x: x["timestamp"])
        return transactions

    def export_csv(self, filepath: str, transactions: List[Dict[str, Any]]):
        """Export dataset to CSV format."""
        df = pd.DataFrame(transactions)
        # Store list fields as JSON strings for CSV compatibility
        df["input_addresses"] = df["input_addresses"].apply(json.dumps)
        df["output_addresses"] = df["output_addresses"].apply(json.dumps)
        df["input_amounts"] = df["input_amounts"].apply(json.dumps)
        df["output_amounts"] = df["output_amounts"].apply(json.dumps)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(df)} transactions to CSV: {filepath}")

    def export_json(self, filepath: str, transactions: List[Dict[str, Any]]):
        """Export dataset to JSON format."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2)
        logger.info(f"Exported {len(transactions)} transactions to JSON: {filepath}")

    def export_xml(self, filepath: str, transactions: List[Dict[str, Any]]):
        """Export dataset to XML format."""
        root = ET.Element("transactions")
        for tx in transactions:
            tx_elem = ET.SubElement(root, "transaction")
            for k, v in tx.items():
                child = ET.SubElement(tx_elem, k)
                if isinstance(v, list):
                    child.text = json.dumps(v)
                else:
                    child.text = str(v)

        xml_str = minidom.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="  ")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
        logger.info(f"Exported {len(transactions)} transactions to XML: {filepath}")
