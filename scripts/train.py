"""
Model training CLI script for CryptoTrace AI.
Trains XGBoost, Isolation Forest, and GraphSAGE models using temporal train/val/test splits.
"""
import os
import sys
import argparse
import json
import yaml
import numpy as np
import pandas as pd
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.xgboost_model import CryptoXGBoostClassifier
from src.models.isolation_forest import CryptoIsolationForest
from src.models.graphsage_model import CryptoGraphSAGE
from src.graph.graph_builder import ForensicGraphBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Train CryptoTrace AI Machine Learning & Graph models.")
    parser.add_argument("--features", type=str, default="data/processed/features.csv", help="Engineered features CSV path")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Configuration YAML path")
    parser.add_argument("--out_dir", type=str, default="models", help="Model weights directory")
    parser.add_argument("--model", type=str, default="all", choices=["all", "xgboost", "isolation_forest", "graphsage"], help="Model to train")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    logger.info(f"Loading features from {args.features}...")
    df = pd.read_csv(args.features)

    # Exclude non-feature metadata columns
    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
    feature_cols = [c for c in df.columns if c not in meta_cols]

    # Filter out unknown labels (label 2) for supervised training if present
    df_supervised = df[df["label"].isin([0, 1])].reset_index(drop=True)
    N = len(df_supervised)

    # Temporal split (chronological): 70% Train, 15% Val, 15% Test
    train_end = int(N * 0.70)
    val_end = int(N * 0.85)

    train_df = df_supervised.iloc[:train_end]
    val_df = df_supervised.iloc[train_end:val_end]
    test_df = df_supervised.iloc[val_end:]

    X_train = train_df[feature_cols].fillna(0.0)
    y_train = train_df["label"].astype(int)

    X_val = val_df[feature_cols].fillna(0.0)
    y_val = val_df["label"].astype(int)

    X_test = test_df[feature_cols].fillna(0.0)
    y_test = test_df["label"].astype(int)

    logger.info(f"Dataset Split -> Train: {len(X_train)} (Positives: {y_train.sum()}), Val: {len(X_val)} (Positives: {y_val.sum()}), Test: {len(X_test)} (Positives: {y_test.sum()})")

    # 1. Train XGBoost
    if args.model in ["all", "xgboost"]:
        logger.info("Training Supervised XGBoost Classifier...")
        xgb_cfg = cfg.get("models", {}).get("xgboost", {})
        xgb_model = CryptoXGBoostClassifier(
            n_estimators=xgb_cfg.get("n_estimators", 200),
            max_depth=xgb_cfg.get("max_depth", 6),
            learning_rate=xgb_cfg.get("learning_rate", 0.05),
            scale_pos_weight=xgb_cfg.get("scale_pos_weight", 10.0),
            random_state=xgb_cfg.get("random_state", 42)
        )
        xgb_report = xgb_model.train(X_train, y_train, X_val, y_val)
        xgb_path = os.path.join(args.out_dir, "xgboost_model.pkl")
        xgb_model.save(xgb_path)

    # 2. Train Isolation Forest
    if args.model in ["all", "isolation_forest"]:
        logger.info("Training Unsupervised Isolation Forest...")
        if_cfg = cfg.get("models", {}).get("isolation_forest", {})
        if_model = CryptoIsolationForest(
            n_estimators=if_cfg.get("n_estimators", 150),
            contamination=if_cfg.get("contamination", 0.08),
            random_state=if_cfg.get("random_state", 42)
        )
        if_report = if_model.train(X_train)
        if_path = os.path.join(args.out_dir, "isolation_forest.pkl")
        if_model.save(if_path)

    # 3. Train GraphSAGE
    if args.model in ["all", "graphsage"]:
        logger.info("Training Graph Neural Network (GraphSAGE)...")
        # Build graph for node representation
        builder = ForensicGraphBuilder()
        G = builder.build_from_dataframe(df_supervised)

        node_list = list(df_supervised["txid"])
        features_mat = df_supervised[feature_cols].fillna(0.0).to_numpy()
        labels_arr = df_supervised["label"].to_numpy()

        train_mask = np.zeros(len(df_supervised), dtype=bool)
        train_mask[:train_end] = True

        val_mask = np.zeros(len(df_supervised), dtype=bool)
        val_mask[train_end:val_end] = True

        gnn_model = CryptoGraphSAGE(
            in_channels=len(feature_cols),
            hidden_channels=64,
            out_channels=2,
            lr=0.005,
            epochs=30
        )
        gnn_report = gnn_model.train(G, node_list, features_mat, labels_arr, train_mask, val_mask)
        gnn_path = os.path.join(args.out_dir, "graphsage.pt")
        gnn_model.save(gnn_path)

    # Save test set for standardized evaluation
    test_out = os.path.join("data/processed", "test_features.csv")
    test_df.to_csv(test_out, index=False)

    logger.info("All model training routines executed successfully!")


if __name__ == "__main__":
    main()
