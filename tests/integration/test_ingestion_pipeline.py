"""
Integration tests for multi-format ingestion pipeline.
"""
from src.cryptotrace.pipelines.ingestion_pipeline import run_ingestion_pipeline


def test_ingestion_pipeline_with_fixture():
    fixture_path = "tests/fixtures/sample_transactions.json"
    df_clean, report = run_ingestion_pipeline(fixture_path)
    assert len(df_clean) == 2
    assert report.valid_rows == 2
    assert "datetime" in df_clean.columns
