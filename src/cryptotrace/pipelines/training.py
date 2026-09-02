"""
End-to-end training pipeline for CryptoTrace AI.
"""
import os
import pandas as pd
import numpy as np
from src.cryptotrace.models.xgboost_model import CryptoXGBoostClassifier
from src.cryptotrace.models.isolation_forest import CryptoIsolationForest
from src.cryptotrace.models.graphsage import CryptoGraphSAGE
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.utils.io import load_yaml
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def run_training_pipeline(
    features_csv: str = "data/processed/features.csv",
    config_yaml: str = "configs/model.yaml",
    models_dir: str = "models"
):
    """Executes chronological split, model fitting, and artifact serialization."""
    os.makedirs(os.path.join(models_dir, "xgboost"), exist_ok=True)
    os.makedirs(os.path.join(models_dir, "isolation_forest"), exist_ok=True)
    os.makedirs(os.path.join(models_dir, "graphsage"), exist_ok=True)

    cfg = load_yaml(config_yaml)
    logger.info(f"Loading features from {features_csv}...")
    df = pd.read_csv(features_csv)

    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
    feature_cols = [c for c in df.columns if c not in meta_cols]

    df_sup = df[df["label"].isin([0, 1])].reset_index(drop=True)
    N = len(df_sup)

    train_end = int(N * 0.70)
    val_end = int(N * 0.85)

    train_df = df_sup.iloc[:train_end]
    val_df = df_sup.iloc[train_end:val_end]
    test_df = df_sup.iloc[val_end:]

    X_train = train_df[feature_cols].fillna(0.0)
    y_train = train_df["label"].astype(int)

    X_val = val_df[feature_cols].fillna(0.0)
    y_val = val_df["label"].astype(int)

    # 1. XGBoost
    logger.info("Fitting XGBoost Classifier...")
    xgb_cfg = cfg.get("xgboost", {})
    xgb_model = CryptoXGBoostClassifier(
        n_estimators=xgb_cfg.get("n_estimators", 200),
        max_depth=xgb_cfg.get("max_depth", 6),
        learning_rate=xgb_cfg.get("learning_rate", 0.05),
        scale_pos_weight=xgb_cfg.get("scale_pos_weight", 10.0),
        random_state=xgb_cfg.get("random_state", 42)
    )
    xgb_model.train(X_train, y_train, X_val, y_val)
    xgb_model.save(os.path.join(models_dir, "xgboost", "xgboost_model.pkl"))

    # 2. Isolation Forest
    logger.info("Fitting Isolation Forest...")
    if_cfg = cfg.get("isolation_forest", {})
    if_model = CryptoIsolationForest(
        n_estimators=if_cfg.get("n_estimators", 150),
        contamination=if_cfg.get("contamination", 0.08),
        random_state=if_cfg.get("random_state", 42)
    )
    if_model.train(X_train)
    if_model.save(os.path.join(models_dir, "isolation_forest", "isolation_forest.pkl"))

    # 3. GraphSAGE
    logger.info("Fitting GraphSAGE GNN...")
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df_sup)

    node_list = list(df_sup["txid"])
    features_mat = df_sup[feature_cols].fillna(0.0).to_numpy()
    labels_arr = df_sup["label"].to_numpy()

    train_mask = np.zeros(len(df_sup), dtype=bool)
    train_mask[:train_end] = True

    gnn_model = CryptoGraphSAGE(
        in_channels=len(feature_cols),
        hidden_channels=64,
        out_channels=2,
        lr=0.005,
        epochs=30
    )
    gnn_model.train(G, node_list, features_mat, labels_arr, train_mask)
    gnn_model.save(os.path.join(models_dir, "graphsage", "graphsage.pt"))

    # Save test partition
    test_df.to_csv("data/processed/test_features.csv", index=False)
    logger.info("Training pipeline completed successfully.")
