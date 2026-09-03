"""CoinJoin / Wasabi / Whirlpool Mixer Heuristic Detector."""

from typing import Dict, Any, List
from collections import Counter


class CoinJoinDetector:
    """Detects CoinJoin mixing transactions based on equal output values and high input/output counts."""

    @staticmethod
    def is_coinjoin(tx_dict: Dict[str, Any], min_equal_outputs: int = 3) -> Dict[str, Any]:
        vins = tx_dict.get("vin", [])
        vouts = tx_dict.get("vout", [])

        if len(vins) < 2 or len(vouts) < 2:
            return {"is_coinjoin": False, "confidence": 0.0, "reason": "Standard transaction structure"}

        # Collect output values
        values = [round(float(out.get("value", 0.0)), 6) for out in vouts]
        val_counts = Counter(values)

        # Look for identical outputs (standard CoinJoin denomination like 0.1 BTC or 0.05 BTC)
        most_common_val, count = val_counts.most_common(1)[0]

        if count >= min_equal_outputs:
            confidence = min(1.0, 0.5 + (count * 0.1))
            return {
                "is_coinjoin": True,
                "confidence": round(confidence, 2),
                "denomination": most_common_val,
                "equal_output_count": count,
                "total_inputs": len(vins),
                "total_outputs": len(vouts),
                "protocol": "Wasabi/Whirlpool/JoinMarket"
            }

        return {"is_coinjoin": False, "confidence": 0.05, "reason": "Variable output amounts"}
