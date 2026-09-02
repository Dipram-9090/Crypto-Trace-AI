"""
Heterogeneous forensic graph constructor.
"""
import networkx as nx
import pandas as pd
from typing import Dict, Any, List
import json
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class ForensicGraphBuilder:
    """Constructs multi-relational graphs across IP, Wallet, Transaction, ASN, and Country entities."""
    def __init__(self):
        self.G = nx.DiGraph()

    def build_from_dataframe(self, df: pd.DataFrame) -> nx.DiGraph:
        self.G.clear()
        if df.empty:
            return self.G

        prev_txid = None
        for idx, row in df.iterrows():
            txid = str(row.get("txid", ""))
            src_ip = str(row.get("src_ip", ""))
            dst_ip = str(row.get("dst_ip", ""))
            src_country = str(row.get("src_country", "Unknown"))
            src_asn = str(row.get("src_asn", "AS0"))
            label = int(row.get("label", 2))
            entity_type = str(row.get("entity_type", "NORMAL_USER"))
            timestamp = str(row.get("timestamp", ""))

            inputs = row.get("input_addresses", [])
            outputs = row.get("output_addresses", [])
            if isinstance(inputs, str):
                try: inputs = json.loads(inputs)
                except Exception: inputs = [inputs]
            if isinstance(outputs, str):
                try: outputs = json.loads(outputs)
                except Exception: outputs = [outputs]

            in_amounts = row.get("input_amounts", [0.0])
            out_amounts = row.get("output_amounts", [0.0])
            if isinstance(in_amounts, str):
                try: in_amounts = json.loads(in_amounts)
                except Exception: in_amounts = [0.0]
            if isinstance(out_amounts, str):
                try: out_amounts = json.loads(out_amounts)
                except Exception: out_amounts = [0.0]

            self.G.add_node(
                txid,
                node_type="Transaction",
                label=label,
                entity_type=entity_type,
                timestamp=timestamp,
                fee=float(row.get("fee", 0.0))
            )

            if src_ip:
                self.G.add_node(src_ip, node_type="IP", country=src_country, asn=src_asn)
                self.G.add_edge(src_ip, txid, relationship="OBSERVED_TRANSACTION")

                if src_asn and src_asn != "AS0":
                    self.G.add_node(src_asn, node_type="ASN")
                    self.G.add_edge(src_ip, src_asn, relationship="BELONGS_TO")

                if src_country and src_country != "Unknown":
                    self.G.add_node(src_country, node_type="Country")
                    self.G.add_edge(src_ip, src_country, relationship="LOCATED_IN")

            if dst_ip and dst_ip != src_ip:
                self.G.add_node(dst_ip, node_type="IP")
                self.G.add_edge(txid, dst_ip, relationship="TRANSMITTED_TO")

            for i_idx, w in enumerate(inputs):
                if w:
                    self.G.add_node(w, node_type="Wallet", label=label, entity_type=entity_type)
                    amt = in_amounts[i_idx] if i_idx < len(in_amounts) else 0.0
                    self.G.add_edge(w, txid, relationship="INPUT_FROM", amount=amt)
                    if src_ip:
                        self.G.add_edge(w, src_ip, relationship="ASSOCIATED_WITH")

            for o_idx, w in enumerate(outputs):
                if w:
                    self.G.add_node(w, node_type="Wallet")
                    amt = out_amounts[o_idx] if o_idx < len(out_amounts) else 0.0
                    self.G.add_edge(txid, w, relationship="OUTPUT_TO", amount=amt)

            if prev_txid:
                self.G.add_edge(prev_txid, txid, relationship="TEMPORALLY_FOLLOWS")
            prev_txid = txid

        return self.G
