"""
CryptoTrace AI Unified Blockchain Forensics Command-Line Interface (CLI).
Supports ingestion, multi-hop graph queries, address clustering, explainable risk scoring,
flow pathfinding, and forensic report generation.
"""

import sys
import os

# Ensure repository root is in sys.path for direct CLI execution
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import argparse
import json
from typing import Optional, Dict, Any
import pandas as pd
from src.cryptotrace.api.app import BlockchainAPIService
from src.cryptotrace.ingestion.csv import load_csv
from src.cryptotrace.ingestion.json import load_json


def _load_service_with_dataset(dataset_path: Optional[str] = None) -> BlockchainAPIService:
    service = BlockchainAPIService()
    path = dataset_path or os.environ.get("CRYPTOTRACE_DATASET") or "data/sample/transactions.csv"
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in [".json", ".jsonl"]:
            df, _ = load_json(path)
        else:
            df, _ = load_csv(path)
        service.ingest_dataframe(df, dataset_id=os.path.basename(path))
    return service


def main():
    parser = argparse.ArgumentParser(
        prog="cryptotrace",
        description="CryptoTrace AI — Offline Bitcoin Blockchain Forensics & Transaction Analysis Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Ingest / Analyze
    p_ingest = subparsers.add_parser("ingest", help="Ingest and validate a dataset file (CSV/JSON/JSONL)")
    p_ingest.add_argument("filepath", help="Path to input dataset file")

    p_analyze = subparsers.add_parser("analyze", help="Run full forensic analysis and risk evaluation on a dataset")
    p_analyze.add_argument("filepath", help="Path to input dataset file")

    # Entity Lookups
    p_tx = subparsers.add_parser("transaction", help="Inspect transaction details and UTXOs")
    p_tx.add_argument("txid", help="Bitcoin Transaction ID (txid)")
    p_tx.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_addr = subparsers.add_parser("address", help="Inspect address profile, balance, and activity")
    p_addr.add_argument("address", help="Bitcoin address")
    p_addr.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_graph = subparsers.add_parser("graph", help="Query k-hop transaction graph neighborhood")
    p_graph.add_argument("identifier", help="Address or Transaction ID")
    p_graph.add_argument("--hops", type=int, default=2, help="Number of expansion hops (default: 2)")
    p_graph.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_risk = subparsers.add_parser("risk", help="Display explainable risk evaluation breakdown")
    p_risk.add_argument("txid", help="Bitcoin Transaction ID")
    p_risk.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_cluster = subparsers.add_parser("cluster", help="Query heuristic common-input address cluster")
    p_cluster.add_argument("identifier", help="Address or Cluster ID")
    p_cluster.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_path = subparsers.add_parser("path", help="Find fund flow paths between source and destination addresses")
    p_path.add_argument("source", help="Source Bitcoin address")
    p_path.add_argument("destination", help="Destination Bitcoin address")
    p_path.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_search = subparsers.add_parser("search", help="Universal search for any identifier")
    p_search.add_argument("query", help="Identifier query string")
    p_search.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    p_report = subparsers.add_parser("report", help="Generate and export forensic investigation report")
    p_report.add_argument("case_id", help="Case ID reference")
    p_report.add_argument("--out", default=None, help="Output markdown file path")
    p_report.add_argument("--dataset", default=None, help="Dataset filepath (default: data/sample/transactions.csv)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command in ["ingest", "analyze"]:
        filepath = args.filepath
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        
        service = BlockchainAPIService()
        ext = os.path.splitext(filepath)[1].lower()
        if ext in [".json", ".jsonl"]:
            df, _ = load_json(filepath)
        else:
            df, _ = load_csv(filepath)

        res = service.ingest_dataframe(df, dataset_id=os.path.basename(filepath))
        print(json.dumps(res, indent=2))

    elif args.command == "transaction":
        service = _load_service_with_dataset(args.dataset)
        res = service.get_transaction(args.txid)
        print(json.dumps(res, indent=2))

    elif args.command == "address":
        service = _load_service_with_dataset(args.dataset)
        res = service.get_address(args.address)
        print(json.dumps(res, indent=2))

    elif args.command == "graph":
        service = _load_service_with_dataset(args.dataset)
        res = service.get_address_graph(args.identifier, k_hops=args.hops)
        print(json.dumps(res, indent=2))

    elif args.command == "risk":
        service = _load_service_with_dataset(args.dataset)
        res = service.get_transaction_risk(args.txid)
        print(json.dumps(res, indent=2))

    elif args.command == "cluster":
        service = _load_service_with_dataset(args.dataset)
        if args.identifier.upper().startswith("CLUSTER_"):
            res = service.get_cluster(args.identifier.upper())
        else:
            addr_res = service.get_address(args.identifier)
            if addr_res.get("success") and addr_res.get("data", {}).get("cluster"):
                res = {"success": True, "data": addr_res["data"]["cluster"]}
            else:
                res = {"success": False, "error": {"code": "NOT_FOUND", "message": "Cluster not found"}}
        print(json.dumps(res, indent=2))

    elif args.command == "path":
        service = _load_service_with_dataset(args.dataset)
        res = service.find_path(args.source, args.destination)
        print(json.dumps(res, indent=2))

    elif args.command == "search":
        service = _load_service_with_dataset(args.dataset)
        res = service.search(args.query)
        print(json.dumps(res, indent=2))

    elif args.command == "report":
        service = _load_service_with_dataset(args.dataset)
        res = service.get_case_report(args.case_id)
        if res.get("success"):
            md = res["data"]["markdown"]
            if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"Report written to {args.out}")
            else:
                print(md)
        else:
            print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
