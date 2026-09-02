"""
Multi-format Ingestion Pipeline (CSV, JSON, XML).
"""

import os
import pandas as pd
from typing import Tuple
from src.cryptotrace.ingestion.csv import load_csv
from src.cryptotrace.ingestion.json import load_json
from src.cryptotrace.ingestion.xml import load_xml
from src.cryptotrace.ingestion.validator import IngestionReport
from src.cryptotrace.preprocessing.cleaning import clean_dataframe


def run_ingestion_pipeline(filepath: str) -> Tuple[pd.DataFrame, IngestionReport]:
    """Ingest, validate, and clean dataset from any supported file format."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".json", ".jsonl"]:
        df_raw, report = load_json(filepath)
    elif ext == ".xml":
        df_raw, report = load_xml(filepath)
    else:
        df_raw, report = load_csv(filepath)

    df_clean = clean_dataframe(df_raw)
    return df_clean, report
