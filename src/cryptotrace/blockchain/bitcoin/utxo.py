"""
Comprehensive UTXO (Unspent Transaction Output) Engine.
Maintains outpoint states, handles spending lifecycle, tracks address balances,
detects double-spends, and estimates transaction fees across ingested blocks and datasets.
"""

from typing import Dict, Optional, List, Set, Tuple, Any
from src.cryptotrace.blockchain.models import UTXO, BitcoinTransaction
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class UTXOSet:
    """In-memory UTXO tracking and ledger engine for forensic blockchain investigation."""

    def __init__(self):
        # Key: "txid:vout" -> UTXO
        self.utxos: Dict[str, UTXO] = {}
        # Address index: address -> set of outpoints ("txid:vout")
        self.address_index: Dict[str, Set[str]] = {}
        # Double-spend detection log: list of flagged double-spend events
        self.double_spends: List[Dict[str, Any]] = []

    def add_utxo(
        self,
        txid: str,
        vout: int,
        address: str,
        amount: float,
        script_type: str = "p2pkh",
        block_height: Optional[int] = None,
        created_at: Optional[str] = None,
    ) -> UTXO:
        """Register a newly created transaction output as an unspent UTXO."""
        outpoint = f"{txid}:{vout}"
        utxo = UTXO(
            txid=txid,
            vout=vout,
            address=address,
            amount=amount,
            script_type=script_type,
            block_height=block_height,
            created_at=created_at,
            is_spent=False,
            spent_in_txid=None,
            spent_at=None,
        )
        self.utxos[outpoint] = utxo
        
        if address:
            if address not in self.address_index:
                self.address_index[address] = set()
            self.address_index[address].add(outpoint)
            
        return utxo

    def spend_utxo(
        self,
        txid: str,
        vout: int,
        spending_txid: str,
        spent_at: Optional[str] = None,
    ) -> Optional[UTXO]:
        """Mark an existing UTXO as spent, checking for potential double-spending."""
        outpoint = f"{txid}:{vout}"
        if outpoint in self.utxos:
            utxo = self.utxos[outpoint]
            if utxo.is_spent:
                # Flag double-spend attempt
                self.double_spends.append({
                    "outpoint": outpoint,
                    "original_spent_in": utxo.spent_in_txid,
                    "attempted_spent_in": spending_txid,
                    "address": utxo.address,
                    "amount": utxo.amount,
                    "timestamp": spent_at,
                })
                logger.warning(f"Double spend detected on outpoint {outpoint} by {spending_txid}")
            utxo.is_spent = True
            utxo.spent_in_txid = spending_txid
            utxo.spent_at = spent_at
            return utxo
        return None

    def process_transaction(self, tx: BitcoinTransaction) -> Tuple[float, float, float]:
        """
        Process a transaction through the UTXO engine:
        1. Mark referenced inputs as spent
        2. Create new UTXOs from outputs
        3. Returns (total_in, total_out, fee)
        """
        total_in = 0.0
        for vin in tx.inputs:
            if vin.prev_txid:
                spent = self.spend_utxo(vin.prev_txid, vin.vout, tx.txid, spent_at=tx.timestamp)
                if spent:
                    total_in += spent.amount
                elif vin.amount > 0:
                    total_in += vin.amount
            elif vin.amount > 0:
                total_in += vin.amount

        total_out = 0.0
        for vout in tx.outputs:
            if not vout.is_op_return:
                self.add_utxo(
                    txid=tx.txid,
                    vout=vout.vout,
                    address=vout.address,
                    amount=vout.amount,
                    script_type=vout.script_type,
                    block_height=tx.block_height,
                    created_at=tx.timestamp,
                )
            total_out += vout.amount

        calculated_fee = max(0.0, total_in - total_out) if total_in >= total_out else tx.fee
        return total_in, total_out, calculated_fee

    def get_utxo(self, txid: str, vout: int) -> Optional[UTXO]:
        """Retrieve a specific UTXO by outpoint."""
        return self.utxos.get(f"{txid}:{vout}")

    def get_unspent_for_address(self, address: str) -> List[UTXO]:
        """Retrieve all currently unspent outputs for a specific address."""
        outpoints = self.address_index.get(address, set())
        return [self.utxos[op] for op in outpoints if op in self.utxos and not self.utxos[op].is_spent]

    def get_all_for_address(self, address: str) -> List[UTXO]:
        """Retrieve all historical outputs (spent and unspent) for an address."""
        outpoints = self.address_index.get(address, set())
        return [self.utxos[op] for op in outpoints if op in self.utxos]

    def get_address_balance(self, address: str) -> float:
        """Calculate the current unspent balance for an address."""
        return sum(u.amount for u in self.get_unspent_for_address(address))

    def get_total_unspent_supply(self) -> float:
        """Sum of all currently unspent UTXOs in the engine."""
        return sum(u.amount for u in self.utxos.values() if not u.is_spent)

    @property
    def total_utxo_count(self) -> int:
        return len(self.utxos)

    @property
    def unspent_count(self) -> int:
        return sum(1 for u in self.utxos.values() if not u.is_spent)

    @property
    def spent_count(self) -> int:
        return sum(1 for u in self.utxos.values() if u.is_spent)
