"""
Integration tests for end-to-end inference pipeline.
"""

import os
import pytest
from src.cryptotrace.pipelines.inference import run_inference_pipeline


def test_inference_pipeline_execution():
    fixture_path = "tests/fixtures/sample_transactions.json"
    assert os.path.exists(fixture_path)

    scored_df, alerts = run_inference_pipeline(
        input_filepath=fixture_path, models_dir="models", config_yaml="configs/config.yaml"
    )

    assert not scored_df.empty
    assert "composite_risk_score" in scored_df.columns
    assert "risk_level" in scored_df.columns
    assert len(scored_df) == 2
