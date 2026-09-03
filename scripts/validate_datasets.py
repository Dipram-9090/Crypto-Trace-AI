"""
Dataset Validation Script

Validates downloaded datasets for integrity, structure, and quality.
Generates comprehensive validation reports.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_ml.src.data.validators import EllipticValidator, BitcoinHeistValidator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    parser = argparse.ArgumentParser(
        description="Validate downloaded datasets"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["elliptic", "bitcoinheist", "all"],
        default="all",
        help="Dataset to validate"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ai_ml/datasets/raw",
        help="Base data directory"
    )
    
    args = parser.parse_args()
    
    results = {}
    
    # Validate Elliptic
    if args.dataset in ["elliptic", "all"]:
        logger.info("Validating Elliptic dataset...")
        validator = EllipticValidator(
            dataset_dir=os.path.join(args.data_dir, "elliptic")
        )
        results["elliptic"] = validator.validate()
    
    # Validate BitcoinHeist
    if args.dataset in ["bitcoinheist", "all"]:
        logger.info("Validating BitcoinHeist dataset...")
        validator = BitcoinHeistValidator(
            dataset_dir=os.path.join(args.data_dir, "bitcoinheist")
        )
        results["bitcoinheist"] = validator.validate()
    
    # Summary
    all_passed = all(results.values())
    logger.info("\n" + "=" * 70)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 70)
    for dataset_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{dataset_name}: {status}")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
