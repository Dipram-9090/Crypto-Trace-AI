"""
Integration tests for ML training and evaluation pipelines.
"""
import os
import pandas as pd
from src.cryptotrace.pipelines.evaluation_pipeline import run_evaluation_pipeline


def test_evaluation_pipeline_execution():
    features_csv = "data/processed/features.csv"
    if os.path.exists(features_csv):
        comp_df = run_evaluation_pipeline(
            features_csv=features_csv,
            models_dir="models",
            out_dir="reports/metrics"
        )
        assert not comp_df.empty
        assert "Model" in comp_df.columns
