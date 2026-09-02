"""
CLI script to generate multi-layer synthetic Bitcoin blockchain, network events, and wallet profiles.
"""
import os
import sys
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generation.synthetic_generator import SyntheticDataGenerator
from src.cryptotrace.storage.parquet_io import write_parquet
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger("generate_synthetic_data")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Bitcoin blockchain & network forensic datasets.")
    parser.add_argument("--transactions", type=int, default=12000, help="Number of transactions (default: 12000)")
    parser.add_argument("--wallets", type=int, default=1200, help="Number of distinct wallets (default: 1200)")
    parser.add_argument("--ips", type=int, default=150, help="Number of IP addresses (default: 150)")
    parser.add_argument("--illicit_ratio", type=float, default=0.08, help="Illicit ratio (default: 0.08)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--out_dir", type=str, default="data/synthetic", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    logger.info(f"Generating {args.transactions} synthetic transactions...")

    generator = SyntheticDataGenerator(
        num_transactions=args.transactions,
        num_wallets=args.wallets,
        num_ips=args.ips,
        illicit_ratio=args.illicit_ratio,
        seed=args.seed
    )

    transactions = generator.generate_transactions()
    generator.export_csv(os.path.join(args.out_dir, "transactions.csv"), transactions)
    generator.export_json(os.path.join(args.out_dir, "transactions.json"), transactions)
    generator.export_xml(os.path.join(args.out_dir, "transactions.xml"), transactions[:500])

    df_tx = pd.read_csv(os.path.join(args.out_dir, "transactions.csv"))
    write_parquet(df_tx, os.path.join(args.out_dir, "transactions.parquet"))

    # 1. Network Events
    logger.info("Generating network_events.csv...")
    net_events = []
    for _, row in df_tx.iterrows():
        net_events.append({
            "event_id": f"EVT_{len(net_events)+1:06d}",
            "timestamp": row["timestamp"],
            "txid": row["txid"],
            "src_ip": row["src_ip"],
            "dst_ip": row["dst_ip"],
            "src_port": row["src_port"],
            "dst_port": row["dst_port"],
            "country": row["src_country"],
            "asn": row["src_asn"]
        })
    df_events = pd.DataFrame(net_events)
    df_events.to_csv(os.path.join(args.out_dir, "network_events.csv"), index=False)
    write_parquet(df_events, os.path.join(args.out_dir, "network_events.parquet"))

    # 2. Wallets Profiles
    logger.info("Generating wallets.csv...")
    wallet_profiles = []
    for w in generator.wallets:
        prof = generator.entities.get(w, {})
        wallet_profiles.append({
            "address": w,
            "entity_type": prof.get("type", "NORMAL_USER"),
            "typical_volume": prof.get("typical_amount", 1.0),
            "reputation_score": 10 if prof.get("type") == "SUSPICIOUS_ACTOR" else 90
        })
    df_wallets = pd.DataFrame(wallet_profiles)
    df_wallets.to_csv(os.path.join(args.out_dir, "wallets.csv"), index=False)
    write_parquet(df_wallets, os.path.join(args.out_dir, "wallets.parquet"))

    # 3. IP-to-Wallet Mapping
    logger.info("Generating ip_wallet_mapping.csv...")
    ip_wallets = []
    for _, row in df_tx.iterrows():
        inputs = eval(row["input_addresses"]) if isinstance(row["input_addresses"], str) and row["input_addresses"].startswith("[") else [row["input_addresses"]]
        for w in inputs:
            ip_wallets.append({"ip": row["src_ip"], "wallet_address": w, "observed_time": row["timestamp"]})
    df_ip_w = pd.DataFrame(ip_wallets).drop_duplicates(subset=["ip", "wallet_address"])
    df_ip_w.to_csv(os.path.join(args.out_dir, "ip_wallet_mapping.csv"), index=False)

    logger.info(f"All synthetic artifacts and Parquet files generated in {args.out_dir}")


if __name__ == "__main__":
    main()
