"""
Data preparation, feature engineering, and graph building CLI script.
"""
import os
import sys
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.ingestion import load_csv, load_json, load_xml
from src.cryptotrace.preprocessing.cleaning import clean_dataframe
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.features.transaction import extract_transaction_features
from src.cryptotrace.features.wallet import WalletTracker
from src.cryptotrace.features.network import NetworkTracker
from src.cryptotrace.features.temporal import TemporalTracker
from src.cryptotrace.features.graph import GraphFeatureExtractor
from src.cryptotrace.storage.parquet_io import write_parquet
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger("prepare_data")


def main():
    parser = argparse.ArgumentParser(description="Ingest raw data, clean, extract features, and build graphs.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Input transaction file path")
    parser.add_argument("--out_dir", type=str, default="data/processed", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    logger.info(f"Ingesting data from {args.input}...")

    ext = os.path.splitext(args.input)[1].lower()
    if ext in [".json", ".jsonl"]:
        df_raw, report = load_json(args.input)
    elif ext == ".xml":
        df_raw, report = load_xml(args.input)
    else:
        df_raw, report = load_csv(args.input)

    logger.info(f"Ingested {report.valid_rows:,} valid records ({report.invalid_rows} invalid, {report.duplicate_rows} duplicates)")

    df_clean = clean_dataframe(df_raw)

    # 1. Build Heterogeneous Graph
    logger.info("Building heterogeneous forensic graph...")
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df_clean)
    logger.info(f"Graph constructed: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # 2. Extract Multi-Modal Features
    logger.info("Extracting transaction, wallet, temporal, network, and graph features...")
    wallet_tracker = WalletTracker()
    network_tracker = NetworkTracker()
    temporal_tracker = TemporalTracker()
    graph_extractor = GraphFeatureExtractor(G)

    rows = []
    for idx, row in df_clean.iterrows():
        r = row.to_dict()
        txid = r.get("txid")
        inputs = r.get("input_addresses", [])
        p_wallet = inputs[0] if isinstance(inputs, list) and len(inputs) > 0 else ""

        t_feats = extract_transaction_features(r)
        w_feats = wallet_tracker.extract_and_update(r)
        n_feats = network_tracker.extract_and_update(r)
        temp_feats = temporal_tracker.extract_and_update(r)
        g_feats = graph_extractor.get_node_features(txid)

        rows.append({
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

    features_df = pd.DataFrame(rows)
    out_csv = os.path.join(args.out_dir, "features.csv")
    out_parquet = os.path.join(args.out_dir, "features.parquet")

    features_df.to_csv(out_csv, index=False)
    write_parquet(features_df, out_parquet)

    logger.info(f"Feature engineering finished! Shape: {features_df.shape}. Output: {out_csv} & {out_parquet}")


if __name__ == "__main__":
    main()
