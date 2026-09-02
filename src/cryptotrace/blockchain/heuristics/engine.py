"""
Forensic Heuristic & Transaction Pattern Detection Engine.
Detects Peel Chains, Mixing-like Patterns, Fan-In/Fan-Out structures, Rapid Velocity,
Dormant Address Activation, and Shannon Transaction Entropy.
"""

import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import numpy as np
from src.cryptotrace.blockchain.models import BitcoinTransaction, ForensicSignal
from src.cryptotrace.blockchain.heuristics.change_detection import ChangeAddressDetector
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


def calculate_shannon_entropy(values: List[float]) -> float:
    """Calculate normalized Shannon entropy over an array of positive values."""
    if not values or len(values) <= 1:
        return 0.0
    total = sum(values)
    if total <= 0:
        return 0.0
    probabilities = [v / total for v in values if v > 0]
    if not probabilities:
        return 0.0
    entropy = -sum(p * math.log2(p) for p in probabilities)
    # Normalize by max possible entropy log2(N)
    max_entropy = math.log2(len(values))
    return round(entropy / max_entropy, 4) if max_entropy > 0 else 0.0


class ForensicHeuristicsEngine:
    """Multi-signal heuristic detection engine for Bitcoin transaction forensics."""

    def __init__(self):
        self.change_detector = ChangeAddressDetector()

    def analyze_transaction(
        self,
        tx: BitcoinTransaction,
        all_transactions: Optional[Dict[str, BitcoinTransaction]] = None,
    ) -> List[ForensicSignal]:
        """
        Evaluate a single Bitcoin transaction across all heuristic forensic indicators.
        Returns a list of explainable ForensicSignal objects.
        """
        signals: List[ForensicSignal] = []

        # 1. Evaluate Change Outputs
        change_evals = self.change_detector.evaluate_outputs(tx)

        # 2. Shannon Entropy of Outputs
        output_values = [o.amount for o in tx.outputs if not o.is_op_return and o.amount > 0]
        entropy = calculate_shannon_entropy(output_values)

        # 3. Fan-Out Detection
        fan_out_count = len(tx.outputs)
        if fan_out_count >= 10:
            severity = "critical" if fan_out_count >= 20 else "high"
            score = 85.0 if fan_out_count >= 20 else 72.0
            signals.append(
                ForensicSignal(
                    type="HIGH_FAN_OUT",
                    severity=severity,
                    score=score,
                    explanation=f"High fan-out dispersion: transaction disperses funds across {fan_out_count} output addresses.",
                    metadata={"fan_out_count": fan_out_count, "total_value": tx.total_output_amount},
                )
            )
        elif fan_out_count >= 5:
            signals.append(
                ForensicSignal(
                    type="MODERATE_FAN_OUT",
                    severity="medium",
                    score=45.0,
                    explanation=f"Moderate fan-out: transaction distributes funds into {fan_out_count} output addresses.",
                    metadata={"fan_out_count": fan_out_count},
                )
            )

        # 4. Fan-In Detection
        fan_in_count = len(tx.inputs)
        if fan_in_count >= 10:
            severity = "critical" if fan_in_count >= 20 else "high"
            score = 80.0 if fan_in_count >= 20 else 68.0
            signals.append(
                ForensicSignal(
                    type="HIGH_FAN_IN",
                    severity=severity,
                    score=score,
                    explanation=f"High fan-in consolidation: transaction aggregates funds from {fan_in_count} input addresses.",
                    metadata={"fan_in_count": fan_in_count, "total_input": tx.total_input_amount},
                )
            )

        # 5. Mixing / CoinJoin-like Pattern Detection
        if fan_in_count >= 3 and fan_out_count >= 3:
            # Check for equal or near-equal value outputs (hallmark of CoinJoin / Whirlpool / Wasabi)
            if len(output_values) >= 3:
                std_dev = float(np.std(output_values))
                mean_val = float(np.mean(output_values))
                cv = (std_dev / mean_val) if mean_val > 0 else 1.0  # Coefficient of variation
                
                # Check for equal values
                rounded_amts = [round(v, 4) for v in output_values]
                most_common_count = max(rounded_amts.count(x) for x in set(rounded_amts))
                
                if cv < 0.15 or most_common_count >= 3 or (entropy > 0.85 and fan_in_count >= 4 and fan_out_count >= 4):
                    signals.append(
                        ForensicSignal(
                            type="MIXING_LIKE_STRUCTURE",
                            severity="high",
                            score=78.0,
                            explanation=(
                                f"Mixing-like pattern detected: Multi-input multi-output structure "
                                f"({fan_in_count} inputs, {fan_out_count} outputs) with high value symmetry "
                                f"({most_common_count} identical-tier outputs, entropy: {entropy:.2f})."
                            ),
                            metadata={
                                "fan_in": fan_in_count,
                                "fan_out": fan_out_count,
                                "entropy": entropy,
                                "coefficient_of_variation": round(cv, 4),
                                "equal_output_tier_count": most_common_count,
                            },
                        )
                    )

        # 6. Peel Chain Step Heuristic (1-2 inputs, 2 outputs where 1 is small change and 1 is larger continuing amount)
        if 1 <= fan_in_count <= 2 and fan_out_count == 2:
            amt1, amt2 = tx.outputs[0].amount, tx.outputs[1].amount
            if amt1 > 0 and amt2 > 0:
                ratio = max(amt1, amt2) / min(amt1, amt2)
                if ratio >= 4.0:
                    signals.append(
                        ForensicSignal(
                            type="PEEL_CHAIN_STEP",
                            severity="medium",
                            score=18.0,
                            explanation=(
                                f"Peel chain transaction step identified: Asymmetrical output split "
                                f"(ratio {ratio:.1f}:1 between {max(amt1, amt2):.4f} BTC and {min(amt1, amt2):.4f} BTC)."
                            ),
                            metadata={
                                "asymmetry_ratio": round(ratio, 2),
                                "primary_amount": max(amt1, amt2),
                                "peeled_amount": min(amt1, amt2),
                            },
                        )
                    )

        # 7. High Value Transfer Heuristic
        if tx.total_output_amount >= 50.0:
            signals.append(
                ForensicSignal(
                    type="LARGE_VALUE_TRANSFER",
                    severity="high",
                    score=20.0,
                    explanation=f"Significant volume transfer: {tx.total_output_amount:.2f} BTC moved in single transaction.",
                    metadata={"amount_btc": tx.total_output_amount},
                )
            )

        # 8. High Fee Anomaly
        if tx.fee >= 0.01:
            signals.append(
                ForensicSignal(
                    type="HIGH_FEE_ANOMALY",
                    severity="medium",
                    score=10.0,
                    explanation=f"Elevated transaction fee observed: {tx.fee:.6f} BTC ({tx.fee_rate:.1f} sat/vB).",
                    metadata={"fee_btc": tx.fee, "fee_rate": tx.fee_rate},
                )
            )

        return signals

    def detect_peel_chains(
        self,
        transactions: List[BitcoinTransaction],
        min_length: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Detect multi-hop peel chains across a sequence of transactions.
        A peel chain repeatedly spends a UTXO to pay a destination while forwarding remainder to a new change address.
        """
        # Map: input_address -> tx
        tx_by_input: Dict[str, List[BitcoinTransaction]] = {}
        tx_by_txid: Dict[str, BitcoinTransaction] = {t.txid: t for t in transactions}

        for tx in transactions:
            for vin in tx.inputs:
                if vin.address:
                    tx_by_input.setdefault(vin.address, []).append(tx)

        detected_chains: List[Dict[str, Any]] = []
        visited_txids: Set[str] = set()

        for tx in transactions:
            if tx.txid in visited_txids:
                continue
            if len(tx.outputs) != 2 or len(tx.inputs) > 2:
                continue

            current_chain = [tx]
            curr_tx = tx

            while True:
                # Find which output might be the change address leading to next hop
                next_tx = None
                for out in curr_tx.outputs:
                    if out.address and out.address in tx_by_input:
                        candidates = [c for c in tx_by_input[out.address] if c.txid != curr_tx.txid and c.txid not in visited_txids]
                        if candidates and len(candidates[0].outputs) == 2:
                            next_tx = candidates[0]
                            break

                if next_tx and next_tx.txid not in [t.txid for t in current_chain]:
                    current_chain.append(next_tx)
                    curr_tx = next_tx
                else:
                    break

            if len(current_chain) >= min_length:
                for c_tx in current_chain:
                    visited_txids.add(c_tx.txid)
                
                initial_amt = current_chain[0].total_input_amount or current_chain[0].total_output_amount
                final_amt = current_chain[-1].total_output_amount
                decay = round((initial_amt - final_amt) / initial_amt * 100.0, 1) if initial_amt > 0 else 0.0

                detected_chains.append({
                    "chain_length": len(current_chain),
                    "start_txid": current_chain[0].txid,
                    "end_txid": current_chain[-1].txid,
                    "transactions": [t.txid for t in current_chain],
                    "initial_value": round(initial_amt, 8),
                    "final_value": round(final_amt, 8),
                    "value_decay_pct": decay,
                    "risk_level": "CRITICAL" if len(current_chain) >= 6 else "HIGH",
                })

        return detected_chains

    def detect_dormant_addresses(
        self,
        transactions: List[BitcoinTransaction],
        dormancy_days_threshold: float = 90.0,
    ) -> List[Dict[str, Any]]:
        """
        Detect addresses with long dormancy periods followed by sudden high-volume activation.
        """
        address_tx_times: Dict[str, List[Tuple[datetime, BitcoinTransaction, str]]] = {}

        for tx in transactions:
            if not tx.timestamp:
                continue
            try:
                ts = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00").split("+")[0])
            except Exception:
                continue

            for vin in tx.inputs:
                if vin.address:
                    address_tx_times.setdefault(vin.address, []).append((ts, tx, "SPEND"))
            for vout in tx.outputs:
                if vout.address:
                    address_tx_times.setdefault(vout.address, []).append((ts, tx, "RECEIVE"))

        dormant_alerts: List[Dict[str, Any]] = []

        for addr, events in address_tx_times.items():
            if len(events) < 2:
                continue
            events.sort(key=lambda x: x[0])
            
            for i in range(len(events) - 1):
                t1, tx1, typ1 = events[i]
                t2, tx2, typ2 = events[i + 1]
                gap_days = (t2 - t1).total_seconds() / 86400.0
                
                if gap_days >= dormancy_days_threshold and tx2.total_output_amount >= 1.0:
                    dormant_alerts.append({
                        "address": addr,
                        "dormancy_duration_days": round(gap_days, 1),
                        "dormancy_start": t1.isoformat(),
                        "activation_time": t2.isoformat(),
                        "activation_txid": tx2.txid,
                        "activation_value": tx2.total_output_amount,
                        "risk_level": "HIGH" if gap_days >= 180 else "MEDIUM",
                    })

        return dormant_alerts

    def detect_rapid_movement(
        self,
        transactions: List[BitcoinTransaction],
        max_interval_seconds: float = 600.0,
    ) -> List[Dict[str, Any]]:
        """
        Detect rapid forwarding / relaying of funds across consecutive transactions within short time windows.
        """
        tx_by_time = []
        for tx in transactions:
            if tx.timestamp:
                try:
                    ts = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00").split("+")[0])
                    tx_by_time.append((ts, tx))
                except Exception:
                    pass

        tx_by_time.sort(key=lambda x: x[0])
        rapid_sequences: List[Dict[str, Any]] = []
        
        # Look for connected tx sequences within short windows
        for i in range(len(tx_by_time) - 1):
            t1, tx1 = tx_by_time[i]
            t2, tx2 = tx_by_time[i + 1]
            diff = (t2 - t1).total_seconds()
            
            # Check if tx1 output address is an input address in tx2
            out_addrs = set(tx1.output_addresses)
            in_addrs = set(tx2.input_addresses)
            overlap = out_addrs.intersection(in_addrs)

            if overlap and 0 <= diff <= max_interval_seconds:
                rapid_sequences.append({
                    "source_txid": tx1.txid,
                    "next_txid": tx2.txid,
                    "relayed_through_address": list(overlap)[0],
                    "interval_seconds": round(diff, 1),
                    "amount": tx2.total_output_amount,
                    "velocity_score": round(max(0.0, 100.0 - (diff / max_interval_seconds * 100.0)), 1),
                })

        return rapid_sequences
