"""
Dataset generation CLI script for CryptoTrace AI.
Generates multi-layer Bitcoin blockchain and network metadata across CSV, JSON, and XML formats.
"""
import os
import sys
import argparse
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generation.synthetic_generator import SyntheticDataGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Bitcoin blockchain & network forensic datasets.")
    parser.add_argument("--transactions", type=int, default=12000, help="Number of transactions to generate (default: 12000)")
    parser.add_argument("--wallets", type=int, default=1200, help="Number of distinct wallets (default: 1200)")
    parser.add_argument("--ips", type=int, default=150, help="Number of IP addresses (default: 150)")
    parser.add_argument("--illicit_ratio", type=float, default=0.08, help="Ratio of suspicious/illicit actors (default: 0.08)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--out_dir", type=str, default="data/synthetic", help="Output directory")

    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    logger.info(f"Generating {args.transactions} synthetic transactions with seed {args.seed}...")
    generator = SyntheticDataGenerator(
        num_transactions=args.transactions,
        num_wallets=args.wallets,
        num_ips=args.ips,
        illicit_ratio=args.illicit_ratio,
        seed=args.seed
    )

    transactions = generator.generate_transactions()
    logger.info(f"Generated {len(transactions)} transactions successfully.")

    csv_path = os.path.join(args.out_dir, "transactions.csv")
    json_path = os.path.join(args.out_dir, "transactions.json")
    xml_path = os.path.join(args.out_dir, "transactions.xml")

    generator.export_csv(csv_path, transactions)
    generator.export_json(json_path, transactions)
    # Generate smaller XML sample (500 records) to keep file sizes clean while demonstrating XML ingestion
    generator.export_xml(xml_path, transactions[:500])

    logger.info(f"Dataset generation complete! Files stored in {args.out_dir}")


if __name__ == "__main__":
    main()
