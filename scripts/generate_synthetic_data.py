"""
CLI script to generate synthetic blockchain and network metadata datasets.
"""
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generation.synthetic_generator import SyntheticDataGenerator
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

    logger.info(f"Datasets generated successfully in {args.out_dir}")


if __name__ == "__main__":
    main()
