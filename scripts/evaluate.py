"""
CLI entry point for model benchmarking and evaluation.
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.models.xgboost_model import CryptoXGBoostClassifier
from src.cryptotrace.models.isolation_forest import CryptoIsolationForest
from src.cryptotrace.models.graphsage import CryptoGraphSAGE
from src.cryptotrace.models.baseline_models import BaselineEvaluator
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.utils.logging import setup_logger
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score

logger = setup_logger("evaluate_cli")


def main():
    parser = argparse.ArgumentParser(description="Evaluate and compare models on temporal test split.")
    parser.add_argument("--features", type=str, default="data/processed/features.csv", help="Full features CSV path")
    parser.add_argument("--models_dir", type=str, default="models", help="Models directory")
    parser.add_argument("--out_dir", type=str, default="reports/metrics", help="Metrics output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.features)
    df_sup = df[df["label"].isin([0, 1])].reset_index(drop=True)

    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
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

    # Baselines
    baseline_eval = BaselineEvaluator(random_state=42)
    b_df = baseline_eval.fit_and_evaluate(X_train, y_train, X_test, y_test)
    for _, r in b_df.iterrows():
        results.append(r.to_dict())

    # XGBoost
    xgb_path = os.path.join(args.models_dir, "xgboost", "xgboost_model.pkl")
    if os.path.exists(xgb_path):
        xgb_model = CryptoXGBoostClassifier.load(xgb_path)
        xgb_eval = xgb_model.evaluate(X_test, y_test)
        results.append({
            "Model": "XGBoost (Primary Classifier)",
            "Precision": round(xgb_eval["precision"], 4),
            "Recall": round(xgb_eval["recall"], 4),
            "F1-Score": round(xgb_eval["f1"], 4),
            "PR-AUC": round(xgb_eval["pr_auc"], 4),
            "ROC-AUC": round(xgb_eval["roc_auc"], 4),
            "Precision@100": xgb_eval.get("precision@100", 0.0),
            "Recall@100": xgb_eval.get("recall@100", 0.0)
        })

    # Isolation Forest
    if_path = os.path.join(args.models_dir, "isolation_forest", "isolation_forest.pkl")
    if os.path.exists(if_path):
        if_model = CryptoIsolationForest.load(if_path)
        anom_scores = if_model.predict_anomaly_score(X_test)
        anom_preds = (anom_scores >= 60.0).astype(int)
        results.append({
            "Model": "Isolation Forest (Anomaly Detection)",
            "Precision": round(float(precision_score(y_test, anom_preds, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test, anom_preds, zero_division=0)), 4),
            "F1-Score": round(float(f1_score(y_test, anom_preds, zero_division=0)), 4),
            "PR-AUC": round(float(average_precision_score(y_test, anom_scores / 100.0)), 4),
            "ROC-AUC": round(float(roc_auc_score(y_test, anom_scores / 100.0)), 4)
        })

    # GraphSAGE
    gnn_path = os.path.join(args.models_dir, "graphsage", "graphsage.pt")
    if os.path.exists(gnn_path):
        gnn_model = CryptoGraphSAGE.load(gnn_path)
        builder = ForensicGraphBuilder()
        G = builder.build_from_dataframe(df_sup)

        node_list = list(df_sup["txid"])
        features_mat = df_sup[feature_cols].fillna(0.0).to_numpy()
        probs = gnn_model.predict_proba(G, node_list, features_mat)

        test_indices = np.arange(val_end, N)
        test_probs = probs[test_indices]
        test_preds = (test_probs >= 0.5).astype(int)

        results.append({
            "Model": "GraphSAGE (Graph Neural Network)",
            "Precision": round(float(precision_score(y_test, test_preds, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test, test_preds, zero_division=0)), 4),
            "F1-Score": round(float(f1_score(y_test, test_preds, zero_division=0)), 4),
            "PR-AUC": round(float(average_precision_score(y_test, test_probs)), 4),
            "ROC-AUC": round(float(roc_auc_score(y_test, test_probs)), 4)
        })

    comp_df = pd.DataFrame(results).fillna("-")
    out_csv = os.path.join(args.out_dir, "model_comparison.csv")
    comp_df.to_csv(out_csv, index=False)
    # Also save to reports/ for dashboard backward compatibility
    comp_df.to_csv("reports/model_comparison.csv", index=False)

    print("\n" + "=" * 80)
    print("                    CRYPTOTRACE AI MODEL BENCHMARK REPORT")
    print("=" * 80)
    print(comp_df.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
