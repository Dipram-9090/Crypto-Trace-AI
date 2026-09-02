"""
CSV ingestion loader for CryptoTrace AI.
"""

from src.cryptotrace.ingestion.csv import load_csv


class CSVLoader:
    """Wrapper for CSV transaction dataset parsing."""

    @staticmethod
    def load(filepath: str):
        return load_csv(filepath)
