"""
Data preparation and feature extraction CLI script for CryptoTrace AI.
Parses raw/synthetic datasets, builds forensic graph, and runs FeaturePipeline.
"""
import os
import sys
import argparse
import pandas as pd
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.csv_parser import parse_csv
from src.ingestion.json_parser import parse_json
from src.ingestion.xml_parser import parse_xml
from src.preprocessing.cleaning import clean_dataframe
from src.graph.graph_builder import ForensicGraphBuilder
from src.features.feature_pipeline import FeaturePipeline
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Ingest and prepare feature matrices for CryptoTrace AI.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Input dataset path")
    parser.add_argument("--out_dir", type=str, default="data/processed", help="Processed data output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Ingestion based on extension
    ext = os.path.splitext(args.input)[1].lower()
    logger.info(f"Ingesting {args.input} ({ext})...")

    if ext == ".json" or ext == ".jsonl":
        df_raw, report = parse_json(args.input)
    elif ext == ".xml":
        df_raw, report = parse_xml(args.input)
    else:
        df_raw, report = parse_csv(args.input)

    logger.info(f"Ingestion Report: {report.to_dict()}")

    # Cleaning and type casting
    df_clean = clean_dataframe(df_raw)

    # Build Graph
    logger.info("Building forensic graph...")
    graph_builder = ForensicGraphBuilder()
    G = graph_builder.build_from_dataframe(df_clean)

    # Extract Features in strict chronological sequence
    logger.info("Extracting multi-modal features...")
    pipeline = FeaturePipeline()
    features_df, feature_names = pipeline.fit_transform(df_clean, G)

    # Save processed outputs
    out_csv = os.path.join(args.out_dir, "features.csv")
    features_df.to_csv(out_csv, index=False)

    meta_path = os.path.join(args.out_dir, "feature_metadata.json")
    import json
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"feature_names": feature_names, "total_records": len(features_df)}, f, indent=2)

    logger.info(f"Data preparation complete! Saved {len(features_df)} rows to {out_csv}")


if __name__ == "__main__":
    main()
