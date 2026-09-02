"""
Bitcoin Transaction Data Structures and Protocol Handling.
Re-exports and extends canonical TxInput, TxOutput, and BitcoinTransaction models.
"""

from typing import List, Optional, Dict, Any
from src.cryptotrace.blockchain.models import TxInput, TxOutput, BitcoinTransaction

__all__ = ["TxInput", "TxOutput", "BitcoinTransaction"]
