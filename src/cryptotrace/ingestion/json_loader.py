"""
JSON & JSONL ingestion loader for CryptoTrace AI.
"""
from src.cryptotrace.ingestion.json import load_json

class JSONLoader:
    """Wrapper for JSON/JSONL transaction dataset parsing."""
    @staticmethod
    def load(filepath: str):
        return load_json(filepath)
