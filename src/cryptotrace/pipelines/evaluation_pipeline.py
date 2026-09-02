"""
Model Benchmark & Temporal Evaluation Pipeline.
"""

import os
import pandas as pd
import numpy as np
from src.cryptotrace.models.xgboost_model import CryptoXGBoostClassifier
from src.cryptotrace.models.isolation_forest import CryptoIsolationForest
from src.cryptotrace.models.graphsage import CryptoGraphSAGE
from src.cryptotrace.models.baseline_models import BaselineEvaluator
from src.cryptotrace.models.ransomware_model import RansomwareClassifier
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.ingestion.bitcoinheist import BitcoinHeistLoader
from src.cryptotrace.storage.parquet_io import write_parquet


def run_evaluation_pipeline(
    features_csv: str = "data/processed/features.csv", models_dir: str = "models", out_dir: str = "reports/metrics"
) -> pd.DataFrame:
    """Evaluates all baseline, supervised, unsupervised, and graph models on held-out temporal splits."""
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(features_csv)
    df_sup = df[df["label"].isin([0, 1])].reset_index(drop=True)

    meta_cols = [
        "txid",
        "timestamp",
        "datetime",
        "src_ip",
        "dst_ip",
        "primary_wallet",
        "src_country",
        "src_asn",
        "label",
        "entity_type",
    ]
    feature_cols = [c for c in df_sup.columns if c not in meta_cols]

    N = len(df_sup)
    train_end = int(N * 0.70)
    val_end = int(N * 0.85)

    train_df = df_sup.iloc[:train_end]
    test_df = df_sup.iloc[val_end:]

    X_train = train_df[feature_cols].fillna(0.0)
    y_train = train_df["label"].astype(int)
    X_test = test_df[feature_cols].fillna(0.0)
    y_test = test_df["label"].astype(int)

    results = []

    # Baseline Evaluator
    baseline_eval = BaselineEvaluator(random_state=42)
    b_df = baseline_eval.fit_and_evaluate(X_train, y_train, X_test, y_test)
    for _, r in b_df.iterrows():
        results.append(r.to_dict())

    # XGBoost
    xgb_path = os.path.join(models_dir, "xgboost", "xgboost_model.pkl")
    if os.path.exists(xgb_path):
        xgb_model = CryptoXGBoostClassifier.load(xgb_path)
        xgb_eval = xgb_model.evaluate(X_test, y_test)
        results.append(
            {
                "Model": "XGBoost (Primary Classifier)",
                "Precision": round(xgb_eval["precision"], 4),
                "Recall": round(xgb_eval["recall"], 4),
                "F1-Score": round(xgb_eval["f1"], 4),
                "PR-AUC": round(xgb_eval["pr_auc"], 4),
                "ROC-AUC": round(xgb_eval["roc_auc"], 4),
                "Precision@100": xgb_eval.get("precision@100", 0.0),
                "Recall@100": xgb_eval.get("recall@100", 0.0),
            }
        )

    comp_df = pd.DataFrame(results)
    out_csv = os.path.join(out_dir, "model_comparison.csv")
    comp_df.to_csv(out_csv, index=False)
    write_parquet(comp_df.astype(str), os.path.join(out_dir, "model_comparison.parquet"))

    return comp_df
