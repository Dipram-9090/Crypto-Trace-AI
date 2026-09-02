"""
Inference and forensic alert generation CLI script for CryptoTrace AI.
Runs end-to-end ingestion, feature extraction, multi-model scoring, SHAP explainability, and ranked alert export.
"""
import os
import sys
import argparse
import json
import pandas as pd
import numpy as np
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.csv_parser import parse_csv
from src.ingestion.json_parser import parse_json
from src.ingestion.xml_parser import parse_xml
from src.preprocessing.cleaning import clean_dataframe
from src.graph.graph_builder import ForensicGraphBuilder
from src.features.feature_pipeline import FeaturePipeline
from src.models.xgboost_model import CryptoXGBoostClassifier
from src.models.isolation_forest import CryptoIsolationForest
from src.models.graphsage_model import CryptoGraphSAGE
from src.explainability.shap_explainer import CryptoSHAPExplainer
from src.scoring.risk_engine import RiskEngine
from src.investigation.alert_generator import AlertGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run end-to-end inference and alert generation on transaction metadata.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Input file path (.csv, .json, .xml)")
    parser.add_argument("--models_dir", type=str, default="models", help="Trained models directory")
    parser.add_argument("--out_dir", type=str, default="reports", help="Reports output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # 1. Ingestion
    ext = os.path.splitext(args.input)[1].lower()
    logger.info(f"Ingesting {args.input}...")
    if ext in [".json", ".jsonl"]:
        df_raw, report = parse_json(args.input)
    elif ext == ".xml":
        df_raw, report = parse_xml(args.input)
    else:
        df_raw, report = parse_csv(args.input)

    df_clean = clean_dataframe(df_raw)

    # 2. Graph & Features
    logger.info("Building graph and extracting features...")
    graph_builder = ForensicGraphBuilder()
    G = graph_builder.build_from_dataframe(df_clean)

    pipeline = FeaturePipeline()
    features_df, feature_names = pipeline.fit_transform(df_clean, G)

    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
    feature_cols = [c for c in features_df.columns if c not in meta_cols]
    X = features_df[feature_cols].fillna(0.0)

    # 3. Model Predictions
    logger.info("Running multi-model predictions...")
    xgb_path = os.path.join(args.models_dir, "xgboost_model.pkl")
    if os.path.exists(xgb_path):
        xgb_model = CryptoXGBoostClassifier.load(xgb_path)
        ml_probs = xgb_model.predict_proba(X)
    else:
        ml_probs = np.zeros(len(X))

    if_path = os.path.join(args.models_dir, "isolation_forest.pkl")
    if os.path.exists(if_path):
        if_model = CryptoIsolationForest.load(if_path)
        anom_scores = if_model.predict_anomaly_score(X)
    else:
        anom_scores = np.zeros(len(X))

    gnn_path = os.path.join(args.models_dir, "graphsage.pt")
    if os.path.exists(gnn_path):
        try:
            gnn_model = CryptoGraphSAGE.load(gnn_path)
            node_list = list(features_df["txid"])
            graph_probs = gnn_model.predict_proba(G, node_list, X.to_numpy()) * 100.0
        except Exception:
            graph_probs = np.zeros(len(X))
    else:
        graph_probs = np.zeros(len(X))

    # 4. Explainability (SHAP)
    logger.info("Computing SHAP explanations for top risk entities...")
    explainer = CryptoSHAPExplainer(xgb_model.model if 'xgb_model' in locals() else None, feature_cols)
    evidence_dict = {}

    # 5. Composite Risk Engine
    risk_engine = RiskEngine.from_config("config/config.yaml")
    composite_scores = []
    risk_tiers = []

    for idx, row in features_df.iterrows():
        prob = float(ml_probs[idx])
        anom = float(anom_scores[idx])
        g_sc = float(graph_probs[idx])

        score, tier = risk_engine.compute_composite_risk(prob, anom, g_sc, row_series=row)
        composite_scores.append(score)
        risk_tiers.append(tier)

        # Generate local evidence for high-risk / critical alerts
        if score >= 40.0:
            evidence_dict[str(row.get("txid"))] = explainer.explain_instance(row, top_k=5)

    features_df["ml_probability"] = ml_probs
    features_df["anomaly_score"] = anom_scores
    features_df["graph_score"] = graph_probs
    features_df["composite_risk_score"] = composite_scores
    features_df["risk_level"] = risk_tiers

    # 6. Ranked Alert Generation
    logger.info("Generating ranked forensic investigative alerts...")
    alert_gen = AlertGenerator(min_risk_threshold=30.0)
    alerts = alert_gen.generate_alerts(features_df, evidence_dict)

    # Export outputs
    out_csv = os.path.join(args.out_dir, "scored_transactions.csv")
    features_df.to_csv(out_csv, index=False)

    out_alerts_json = os.path.join(args.out_dir, "ranked_alerts.json")
    with open(out_alerts_json, "w", encoding="utf-8") as f:
        json.dump([a.to_dict() for a in alerts], f, indent=2)

    logger.info(f"Inference complete! {len(alerts)} alerts generated. Saved results to {args.out_dir}")
    print(f"\n[OK] Top Ranked Forensic Leads:")
    for a in alerts[:5]:
        print(f"  [{a.alert_id}] {a.risk_level} (Risk: {a.risk_score}/100 | ML: {a.ml_probability:.2f}) -> Entity: {a.entity_id}")


if __name__ == "__main__":
    main()
