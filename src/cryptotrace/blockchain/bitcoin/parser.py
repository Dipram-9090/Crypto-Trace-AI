"""
Raw Bitcoin transaction deserializer and JSON-RPC response parser.
"""

from typing import Dict, Any
from src.cryptotrace.blockchain.bitcoin.transaction import BitcoinTransaction, TxInput, TxOutput


def parse_rpc_raw_transaction(tx_dict: Dict[str, Any]) -> BitcoinTransaction:
    """Parse JSON representation from getrawtransaction RPC into BitcoinTransaction."""
    txid = tx_dict.get("txid", "")
    inputs = []
    for vin in tx_dict.get("vin", []):
        inputs.append(
            TxInput(prev_txid=vin.get("txid", ""), vout=vin.get("vout", 0), sequence=vin.get("sequence", 0xFFFFFFFF))
        )

    outputs = []
    for vout in tx_dict.get("vout", []):
        spk = vout.get("scriptPubKey", {})
        addrs = spk.get("addresses", [spk.get("address", "")])
        primary_addr = addrs[0] if addrs and addrs[0] else ""
        outputs.append(
            TxOutput(
                address=primary_addr,
                amount=float(vout.get("value", 0.0)),
                vout=int(vout.get("n", 0)),
                script_pubkey=spk.get("hex", ""),
                script_type=spk.get("type", "p2pkh"),
            )
        )

    return BitcoinTransaction(
        txid=txid,
        version=int(tx_dict.get("version", 2)),
        locktime=int(tx_dict.get("locktime", 0)),
        inputs=inputs,
        outputs=outputs,
    )
