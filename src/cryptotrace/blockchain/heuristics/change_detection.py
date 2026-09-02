"""
Change Address Heuristic Detection Engine.
Calculates change_probability (0.0 to 1.0) for transaction outputs based on:
1. Address reuse and self-spending patterns
2. Script type matching between inputs and outputs
3. Round-number payment heuristic (payment values are round decimals; change is remainder)
4. Value asymmetry and size decay heuristics.
"""

from typing import Dict, List, Any, Optional
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxOutput


class ChangeAddressDetector:
    """Forensic heuristic analyzer for identifying change outputs in Bitcoin transactions."""

    def __init__(self):
        self.address_history: Dict[str, int] = {}

    def record_transaction(self, tx: BitcoinTransaction):
        """Update address occurrence frequency across the dataset."""
        for vin in tx.inputs:
            if vin.address:
                self.address_history[vin.address] = self.address_history.get(vin.address, 0) + 1
        for vout in tx.outputs:
            if vout.address:
                self.address_history[vout.address] = self.address_history.get(vout.address, 0) + 1

    def is_round_number(self, amount: float) -> bool:
        """Check if an amount looks like an intentional round payment (e.g., 0.1, 0.5, 1.0, 5.0)."""
        if amount <= 0:
            return False
        # Check integer amounts or 1-2 decimal round steps
        satoshis = round(amount * 1e8)
        if satoshis % 100_000_000 == 0:  # whole BTC
            return True
        if satoshis % 10_000_000 == 0:  # 0.1 BTC steps
            return True
        if satoshis % 1_000_000 == 0:  # 0.01 BTC steps
            return True
        if satoshis % 100_000 == 0:  # 0.001 BTC steps
            return True
        return False

    def evaluate_outputs(self, tx: BitcoinTransaction) -> List[Dict[str, Any]]:
        """
        Evaluate each output of a transaction and assign a change_probability with forensic rationale.
        """
        results: List[Dict[str, Any]] = []
        if len(tx.outputs) == 0:
            return results

        # 1-output transactions have no change (or 100% sweep)
        if len(tx.outputs) == 1:
            out = tx.outputs[0]
            is_self_spend = any(vin.address == out.address for vin in tx.inputs if vin.address)
            prob = 0.95 if is_self_spend else 0.05
            results.append({
                "vout": out.vout,
                "address": out.address,
                "amount": out.amount,
                "change_probability": prob,
                "reasons": ["Single output transaction (likely direct transfer or consolidation)"],
            })
            return results

        input_script_types = set(vin.script_type for vin in tx.inputs if vin.script_type)
        input_addresses = set(vin.address for vin in tx.inputs if vin.address)

        for out in tx.outputs:
            if out.is_op_return or not out.address:
                results.append({
                    "vout": out.vout,
                    "address": out.address or "OP_RETURN",
                    "amount": out.amount,
                    "change_probability": 0.0,
                    "reasons": ["OP_RETURN data output cannot be change address"],
                })
                continue

            score = 0.5  # Base neutral prior
            reasons = []

            # 1. Self-spending check (address reuse directly in inputs)
            if out.address in input_addresses:
                score += 0.40
                reasons.append("Address is identical to an input address (explicit self-change or consolidation)")

            # 2. Script type matching
            if out.script_type in input_script_types and len(input_script_types) == 1:
                score += 0.15
                reasons.append(f"Output script type ({out.script_type}) matches input script type")
            elif input_script_types and out.script_type not in input_script_types:
                score -= 0.20
                reasons.append(f"Output script type ({out.script_type}) differs from input script types")

            # 3. Round number heuristic
            other_outputs = [o for o in tx.outputs if o.vout != out.vout and not o.is_op_return]
            if not self.is_round_number(out.amount) and any(self.is_round_number(o.amount) for o in other_outputs):
                score += 0.25
                reasons.append("Non-round amount while counterpart output has round payment value")
            elif self.is_round_number(out.amount) and any(not self.is_round_number(o.amount) for o in other_outputs):
                score -= 0.25
                reasons.append("Round payment value (typical merchant or peer payment amount)")

            # 4. Fresh address vs reused address
            addr_history_count = self.address_history.get(out.address, 0)
            if addr_history_count <= 1:
                score += 0.10
                reasons.append("Fresh unique address (standard HD wallet change address behavior)")
            else:
                score -= 0.10
                reasons.append("Reused address across multiple transactions")

            # Clamp probability
            final_prob = max(0.01, min(0.99, round(score, 2)))
            
            # Update output object
            out.change_probability = final_prob
            out.is_change = final_prob >= 0.65

            results.append({
                "vout": out.vout,
                "address": out.address,
                "amount": out.amount,
                "change_probability": final_prob,
                "is_likely_change": out.is_change,
                "reasons": reasons,
            })

        return results
