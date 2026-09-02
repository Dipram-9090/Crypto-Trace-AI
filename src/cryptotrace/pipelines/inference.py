"""
End-to-end inference and investigative triage pipeline.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from src.cryptotrace.ingestion import load_csv, load_json, load_xml
from src.cryptotrace.preprocessing.cleaning import clean_dataframe
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.features.transaction import extract_transaction_features
from src.cryptotrace.features.wallet import WalletTracker
from src.cryptotrace.features.network import NetworkTracker
from src.cryptotrace.features.temporal import TemporalTracker
from src.cryptotrace.features.graph import GraphFeatureExtractor
from src.cryptotrace.models.xgboost_model import CryptoXGBoostClassifier
from src.cryptotrace.models.isolation_forest import CryptoIsolationForest
from src.cryptotrace.models.graphsage import CryptoGraphSAGE
from src.cryptotrace.explainability.shap import CryptoSHAPExplainer
from src.cryptotrace.scoring.risk_engine import RiskEngine
from src.cryptotrace.utils.io import save_json
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def run_inference_pipeline(
    input_filepath: str,
    models_dir: str = "models",
    config_yaml: str = "configs/config.yaml"
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Ingests data, extracts multi-modal features, computes risk scores, and generates alerts."""
    ext = os.path.splitext(input_filepath)[1].lower()
    if ext in [".json", ".jsonl"]:
        df_raw, _ = load_json(input_filepath)
    elif ext == ".xml":
        df_raw, _ = load_xml(input_filepath)
    else:
        df_raw, _ = load_csv(input_filepath)

    df_clean = clean_dataframe(df_raw)

    # Build Graph
    graph_builder = ForensicGraphBuilder()
    G = graph_builder.build_from_dataframe(df_clean)

    # Feature extraction
    wallet_tracker = WalletTracker()
    network_tracker = NetworkTracker()
    temporal_tracker = TemporalTracker()
    graph_extractor = GraphFeatureExtractor(G)

    records = []
    for idx, row in df_clean.iterrows():
        r = row.to_dict()
        txid = r.get("txid")
        p_wallet = r.get("input_addresses", [""])[0] if r.get("input_addresses") else ""

        t_feats = extract_transaction_features(r)
        w_feats = wallet_tracker.extract_and_update(r)
        n_feats = network_tracker.extract_and_update(r)
        temp_feats = temporal_tracker.extract_and_update(r)
        g_feats = graph_extractor.get_node_features(txid)

        records.append({
            "txid": txid,
            "timestamp": r.get("timestamp"),
            "datetime": r.get("datetime"),
            "src_ip": r.get("src_ip"),
            "dst_ip": r.get("dst_ip"),
            "primary_wallet": p_wallet,
            "src_country": r.get("src_country"),
            "src_asn": r.get("src_asn"),
            "label": int(r.get("label", 2)),
            "entity_type": str(r.get("entity_type", "NORMAL_USER")),
            **t_feats,
            **w_feats,
            **n_feats,
            **temp_feats,
            **g_feats
        })

    feat_df = pd.DataFrame(records)
    meta_cols = ["txid", "timestamp", "datetime", "src_ip", "dst_ip", "primary_wallet", "src_country", "src_asn", "label", "entity_type"]
    feature_cols = [c for c in feat_df.columns if c not in meta_cols]
    X = feat_df[feature_cols].fillna(0.0)

    # Load models
    xgb_path = os.path.join(models_dir, "xgboost", "xgboost_model.pkl")
    if_path = os.path.join(models_dir, "isolation_forest", "isolation_forest.pkl")
    gnn_path = os.path.join(models_dir, "graphsage", "graphsage.pt")

    ml_probs = CryptoXGBoostClassifier.load(xgb_path).predict_proba(X) if os.path.exists(xgb_path) else np.zeros(len(X))
    anom_scores = CryptoIsolationForest.load(if_path).predict_anomaly_score(X) if os.path.exists(if_path) else np.zeros(len(X))
    
    if os.path.exists(gnn_path):
        try:
            gnn = CryptoGraphSAGE.load(gnn_path)
            node_list = list(feat_df["txid"])
            graph_probs = gnn.predict_proba(G, node_list, X.to_numpy()) * 100.0
        except Exception:
            graph_probs = np.zeros(len(X))
    else:
        graph_probs = np.zeros(len(X))

    # Risk Engine & SHAP
    risk_engine = RiskEngine.from_config(config_yaml)
    explainer = CryptoSHAPExplainer(CryptoXGBoostClassifier.load(xgb_path).model if os.path.exists(xgb_path) else None, feature_cols)

    composite_scores, risk_tiers = [], []
    alerts = []

    for idx, row in feat_df.iterrows():
        prob = float(ml_probs[idx])
        anom = float(anom_scores[idx])
        g_sc = float(graph_probs[idx])

        score, tier = risk_engine.compute_composite_risk(prob, anom, g_sc, row_series=row)
        composite_scores.append(score)
        risk_tiers.append(tier)

        if score >= 30.0:
            evidence = explainer.explain_instance(row, top_k=5)
            alerts.append({
                "alert_id": f"ALERT_{len(alerts)+1:04d}",
                "entity_type": "Wallet" if row.get("primary_wallet") else "Transaction",
                "entity_id": str(row.get("primary_wallet") or row.get("txid")),
                "txid": str(row.get("txid")),
                "risk_score": score,
                "risk_level": tier,
                "ml_probability": round(prob, 4),
                "anomaly_score": round(anom, 1),
                "graph_score": round(g_sc, 1),
                "top_features": evidence,
                "src_ip": str(row.get("src_ip")),
                "src_country": str(row.get("src_country")),
                "src_asn": str(row.get("src_asn")),
                "timestamp": str(row.get("timestamp"))
            })

    feat_df["ml_probability"] = ml_probs
    feat_df["anomaly_score"] = anom_scores
    feat_df["graph_score"] = graph_probs
    feat_df["composite_risk_score"] = composite_scores
    feat_df["risk_level"] = risk_tiers

    alerts.sort(key=lambda x: x["risk_score"], reverse=True)
    return feat_df, alerts
