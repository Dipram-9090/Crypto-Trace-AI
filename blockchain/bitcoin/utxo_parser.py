"""Bitcoin UTXO and Script Parser."""

from typing import Dict, Any, List


class BitcoinUTXOParser:
    """Parses raw Bitcoin transaction outputs and scripts."""

    @staticmethod
    def extract_outputs(tx_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        outputs = []
        for out in tx_dict.get("vout", []):
            script = out.get("scriptPubKey", {})
            addr = script.get("address") or script.get("addresses", ["unknown"])[0]
            val = float(out.get("value", 0.0))
            script_type = script.get("type", "pubkeyhash")

            outputs.append({
                "n": out.get("n", 0),
                "address": addr,
                "value_btc": val,
                "script_type": script_type,
                "is_op_return": script_type == "nulldata"
            })
        return outputs
