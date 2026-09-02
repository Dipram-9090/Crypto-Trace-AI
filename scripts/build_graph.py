"""
Heterogeneous Graph Construction and Serialization CLI.
"""
import os
import sys
import argparse
import pandas as pd
import networkx as nx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger("build_graph_cli")


def main():
    parser = argparse.ArgumentParser(description="Construct and analyze heterogeneous forensic graph.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Input transaction CSV")
    parser.add_argument("--out_dir", type=str, default="reports/figures", help="Graph output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.input)
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df)

    logger.info(f"Graph constructed: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


if __name__ == "__main__":
    main()
