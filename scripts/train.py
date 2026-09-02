"""
CLI entry point for model training pipeline.
"""
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.pipelines.training import run_training_pipeline
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger("train_cli")


def main():
    parser = argparse.ArgumentParser(description="Train CryptoTrace AI Machine Learning and Graph models.")
    parser.add_argument("--features", type=str, default="data/processed/features.csv", help="Features CSV path")
    parser.add_argument("--config", type=str, default="configs/model.yaml", help="Configuration YAML path")
    parser.add_argument("--out_dir", type=str, default="models", help="Model weights directory")
    args = parser.parse_args()

    logger.info("Initiating CryptoTrace AI Model Training Pipeline...")
    run_training_pipeline(
        features_csv=args.features,
        config_yaml=args.config,
        models_dir=args.out_dir
    )
    logger.info("Training pipeline finished.")


if __name__ == "__main__":
    main()
