"""
UTXO (Unspent Transaction Output) Set & Peeling Chain Tracking.
"""

from typing import Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class UTXO:
    txid: str
    vout: int
    address: str
    amount: float
    is_spent: bool = False
    spent_in_txid: Optional[str] = None


class UTXOSet:
    """In-memory UTXO tracker for identifying consolidation and peeling chains."""

    def __init__(self):
        self.utxos: Dict[str, UTXO] = {}

    def add_utxo(self, txid: str, vout: int, address: str, amount: float):
        key = f"{txid}:{vout}"
        self.utxos[key] = UTXO(txid=txid, vout=vout, address=address, amount=amount)

    def spend_utxo(self, txid: str, vout: int, spending_txid: str) -> Optional[UTXO]:
        key = f"{txid}:{vout}"
        if key in self.utxos:
            utxo = self.utxos[key]
            utxo.is_spent = True
            utxo.spent_in_txid = spending_txid
            return utxo
        return None

    def get_address_balance(self, address: str) -> float:
        return sum(u.amount for u in self.utxos.values() if u.address == address and not u.is_spent)
