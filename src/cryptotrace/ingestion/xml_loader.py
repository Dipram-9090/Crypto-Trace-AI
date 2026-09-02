"""
XML ingestion loader for CryptoTrace AI.
"""

from src.cryptotrace.ingestion.xml import load_xml


class XMLLoader:
    """Wrapper for XML transaction dataset parsing."""

    @staticmethod
    def load(filepath: str):
        return load_xml(filepath)
