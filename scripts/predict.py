"""
CLI entry point for inference and alert triage generation.
"""
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cryptotrace.pipelines.inference import run_inference_pipeline
from src.cryptotrace.utils.io import save_json
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger("predict_cli")


def main():
    parser = argparse.ArgumentParser(description="Execute inference and alert prioritization on transactions.")
    parser.add_argument("--input", type=str, default="data/synthetic/transactions.csv", help="Input transaction file (.csv, .json, .xml)")
    parser.add_argument("--models_dir", type=str, default="models", help="Trained models directory")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Config file path")
    parser.add_argument("--out_dir", type=str, default="reports", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    logger.info(f"Running inference on {args.input}...")

    scored_df, alerts = run_inference_pipeline(
        input_filepath=args.input,
        models_dir=args.models_dir,
        config_yaml=args.config
    )

    scored_df.to_csv(os.path.join(args.out_dir, "scored_transactions.csv"), index=False)
    save_json(alerts, os.path.join(args.out_dir, "ranked_alerts.json"))

    logger.info(f"Inference completed! {len(alerts)} alerts generated.")
    print(f"\n[OK] Top Prioritized Leads:")
    for a in alerts[:5]:
        print(f"  [{a['alert_id']}] {a['risk_level']} (Score: {a['risk_score']}/100 | ML: {a['ml_probability']}) -> Entity: {a['entity_id']}")


if __name__ == "__main__":
    main()
