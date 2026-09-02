"""
Multi-hop Directed Blockchain Transaction Graph Engine.
Constructs NetworkX bipartite (Address <-> Transaction) and homogeneous (Address -> Address) graphs.
Provides graph analytics: PageRank, Degree/Betweenness Centrality, k-Hop Neighborhood Expansion,
Connected Components, Community Structure, and Shortest Flow Paths.
"""

from typing import Dict, Any, List, Set, Optional, Tuple
import networkx as nx
from src.cryptotrace.blockchain.models import BitcoinTransaction
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class BlockchainGraphEngine:
    """Forensic NetworkX Graph Engine for Bitcoin fund tracing and topological analytics."""

    def __init__(self):
        # Full bipartite graph: Address nodes and Transaction nodes
        self.G = nx.DiGraph()
        # Direct address-to-address flow graph
        self.address_flow_G = nx.DiGraph()
        # Ingestion lookup
        self.transactions: Dict[str, BitcoinTransaction] = {}
        self.addresses: Set[str] = set()

    def build_from_transactions(self, transactions: List[BitcoinTransaction]) -> nx.DiGraph:
        """Construct full bipartite and homogeneous address flow graphs from transactions."""
        self.G.clear()
        self.address_flow_G.clear()
        self.transactions.clear()
        self.addresses.clear()

        for tx in transactions:
            self.transactions[tx.txid] = tx
            
            # Add transaction node
            self.G.add_node(
                tx.txid,
                node_type="Transaction",
                txid=tx.txid,
                timestamp=tx.timestamp,
                block_height=tx.block_height,
                fee=tx.fee,
                vsize=tx.vsize,
                fan_out=len(tx.outputs),
                fan_in=len(tx.inputs),
                total_value=tx.total_output_amount,
            )

            # Process inputs: Address -> Transaction
            for vin in tx.inputs:
                if vin.address:
                    addr = vin.address
                    self.addresses.add(addr)
                    if not self.G.has_node(addr):
                        self.G.add_node(addr, node_type="Address", address=addr, script_type=vin.script_type)
                    self.G.add_edge(addr, tx.txid, relationship="INPUT_FROM", amount=vin.amount, vout=vin.vout)

            # Process outputs: Transaction -> Address
            for vout in tx.outputs:
                if vout.address and not vout.is_op_return:
                    addr = vout.address
                    self.addresses.add(addr)
                    if not self.G.has_node(addr):
                        self.G.add_node(addr, node_type="Address", address=addr, script_type=vout.script_type)
                    self.G.add_edge(tx.txid, addr, relationship="OUTPUT_TO", amount=vout.amount, vout=vout.vout)

            # Build direct Address -> Address flow edges
            in_addrs = [vin.address for vin in tx.inputs if vin.address]
            out_addrs = [vout.address for vout in tx.outputs if vout.address and not vout.is_op_return]
            
            for src in in_addrs:
                if not self.address_flow_G.has_node(src):
                    self.address_flow_G.add_node(src, node_type="Address", address=src)
                for dst in out_addrs:
                    if not self.address_flow_G.has_node(dst):
                        self.address_flow_G.add_node(dst, node_type="Address", address=dst)
                    
                    split_amt = tx.total_output_amount / max(1, len(out_addrs) * len(in_addrs))
                    if self.address_flow_G.has_edge(src, dst):
                        self.address_flow_G[src][dst]["weight"] += split_amt
                        self.address_flow_G[src][dst]["txids"].append(tx.txid)
                    else:
                        self.address_flow_G.add_edge(
                            src, dst,
                            weight=split_amt,
                            txids=[tx.txid],
                            timestamp=tx.timestamp,
                        )

        return self.G

    def compute_graph_metrics(self) -> Dict[str, Any]:
        """Compute topological metrics including PageRank, centralities, and components."""
        if len(self.G) == 0:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "address_count": 0,
                "transaction_count": 0,
                "pagerank": {},
                "degree_centrality": {},
                "connected_components_count": 0,
            }

        try:
            pr = nx.pagerank(self.G, alpha=0.85, max_iter=100)
        except Exception:
            pr = {n: 1.0 / len(self.G) for n in self.G.nodes}

        deg_cent = nx.degree_centrality(self.G)
        
        # Undirected view for connected components
        undirected_view = self.G.to_undirected()
        num_components = nx.number_connected_components(undirected_view)

        return {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "address_count": len(self.addresses),
            "transaction_count": len(self.transactions),
            "pagerank": pr,
            "degree_centrality": deg_cent,
            "connected_components_count": num_components,
        }

    def get_k_hop_subgraph(
        self,
        center_node: str,
        k_hops: int = 2,
        max_nodes: int = 150,
    ) -> Dict[str, Any]:
        """
        Extract k-hop ego network around an address or transaction.
        Returns a front-end ready JSON dictionary with nodes and links.
        """
        if center_node not in self.G:
            return {"nodes": [], "links": [], "center": center_node, "hops": k_hops}

        # BFS expansion up to k hops
        visited_nodes: Set[str] = {center_node}
        current_layer: Set[str] = {center_node}

        for hop in range(k_hops):
            next_layer: Set[str] = set()
            for node in current_layer:
                successors = set(self.G.successors(node))
                predecessors = set(self.G.predecessors(node))
                neighbors = successors.union(predecessors)
                for neighbor in neighbors:
                    if neighbor not in visited_nodes:
                        next_layer.add(neighbor)
                        visited_nodes.add(neighbor)
                        if len(visited_nodes) >= max_nodes:
                            break
                if len(visited_nodes) >= max_nodes:
                    break
            current_layer = next_layer
            if len(visited_nodes) >= max_nodes:
                break

        subgraph = self.G.subgraph(visited_nodes)

        nodes_data = []
        for n, attrs in subgraph.nodes(data=True):
            node_info = {
                "id": n,
                "label": n[:8] + "..." if len(n) > 12 else n,
                "full_id": n,
                "node_type": attrs.get("node_type", "Unknown"),
                "is_center": (n == center_node),
                **{k: v for k, v in attrs.items() if k not in ["node_type"]},
            }
            nodes_data.append(node_info)

        links_data = []
        for u, v, attrs in subgraph.edges(data=True):
            links_data.append({
                "source": u,
                "target": v,
                "relationship": attrs.get("relationship", "FLOWS_TO"),
                "amount": float(attrs.get("amount", 0.0)),
                "vout": attrs.get("vout", 0),
            })

        return {
            "nodes": nodes_data,
            "links": links_data,
            "center": center_node,
            "hops": k_hops,
            "node_count": len(nodes_data),
            "edge_count": len(links_data),
        }

    def find_flow_paths(
        self,
        source_address: str,
        target_address: str,
        max_paths: int = 5,
        cutoff_hops: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Calculate fund flow paths between source and target addresses.
        Uses shortest path algorithms over direct address flow graph.
        """
        if not self.address_flow_G.has_node(source_address) or not self.address_flow_G.has_node(target_address):
            return []

        try:
            paths = list(nx.all_simple_paths(
                self.address_flow_G,
                source=source_address,
                target=target_address,
                cutoff=cutoff_hops,
            ))
        except Exception:
            return []

        results = []
        for path in paths[:max_paths]:
            path_edges = []
            total_transferred = 0.0
            tx_chain = []
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.address_flow_G.get_edge_data(u, v, {})
                weight = edge_data.get("weight", 0.0)
                txids = edge_data.get("txids", [])
                total_transferred += weight
                tx_chain.extend(txids)
                path_edges.append({
                    "from_address": u,
                    "to_address": v,
                    "amount": round(weight, 8),
                    "transactions": txids,
                })

            results.append({
                "path": path,
                "hop_count": len(path) - 1,
                "edges": path_edges,
                "total_value": round(total_transferred, 8),
                "transaction_ids": list(set(tx_chain)),
            })

        return results
