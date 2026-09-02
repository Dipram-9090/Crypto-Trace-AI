"""
Forensic graph builder CLI script for CryptoTrace AI.
Builds and serializes the heterogeneous blockchain and network graph from transaction records.
"""
import os
import sys
import argparse
import pandas as pd
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.csv_parser import parse_csv
from src.preprocessing.cleaning import clean_dataframe
from src.graph.graph_builder import ForensicGraphBuilder
import networkx as nx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Construct and export forensic graph.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Transaction CSV path")
    parser.add_argument("--out_file", type=str, default="data/processed/forensic_graph.gml", help="Graph output path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out_file), exist_ok=True)

    df_raw, _ = parse_csv(args.input)
    df_clean = clean_dataframe(df_raw)

    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df_clean)

    logger.info(f"Writing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges to {args.out_file}...")
    # Store simple graph
    nx.write_gml(G, args.out_file)
    logger.info("Graph exported successfully.")


if __name__ == "__main__":
    main()
