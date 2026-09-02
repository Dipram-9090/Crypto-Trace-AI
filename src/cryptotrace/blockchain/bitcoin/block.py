"""
Bitcoin Block Data Structure and Header Extraction.
"""

from dataclasses import dataclass, field
from typing import List
from src.cryptotrace.blockchain.bitcoin.transaction import BitcoinTransaction


@dataclass
class BitcoinBlock:
    hash: str
    height: int
    version: int
    merkle_root: str
    timestamp: int
    bits: int
    nonce: int
    transactions: List[BitcoinTransaction] = field(default_factory=list)

    @property
    def transaction_count(self) -> int:
        return len(self.transactions)
