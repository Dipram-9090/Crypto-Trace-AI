"""
Bitcoin Transaction Data Structures and UTXO Handling.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TxInput:
    prev_txid: str
    vout: int
    script_sig: str = ""
    sequence: int = 0xFFFFFFFF
    address: Optional[str] = None
    amount: float = 0.0


@dataclass
class TxOutput:
    address: str
    amount: float
    vout: int
    script_pubkey: str = ""
    script_type: str = "p2pkh"


@dataclass
class BitcoinTransaction:
    txid: str
    version: int = 2
    locktime: int = 0
    inputs: List[TxInput] = field(default_factory=list)
    outputs: List[TxOutput] = field(default_factory=list)
    fee: float = 0.0
    timestamp: Optional[str] = None

    @property
    def total_input_amount(self) -> float:
        return sum(i.amount for i in self.inputs)

    @property
    def total_output_amount(self) -> float:
        return sum(o.amount for o in self.outputs)

    @property
    def fan_out_ratio(self) -> float:
        return len(self.outputs) / len(self.inputs) if len(self.inputs) > 0 else float(len(self.outputs))
