"""
Common-Input Ownership Heuristic Clustering Engine.
Aggregates co-spending Bitcoin addresses into candidate entity clusters (connected components).
Explicitly marks all clusters as heuristic inferences rather than confirmed identities.
"""

from typing import Dict, List, Set, Optional, Any
import networkx as nx
from src.cryptotrace.blockchain.models import BitcoinTransaction, AddressCluster
from src.cryptotrace.utils.logging import setup_logger

logger = setup_logger(__name__)


class CommonInputClusterer:
    """Heuristic address clustering engine implementing the Common-Input Ownership rule."""

    def __init__(self):
        self.co_spend_graph = nx.Graph()
        self.address_to_cluster_id: Dict[str, str] = {}
        self.clusters: Dict[str, AddressCluster] = {}

    def cluster_transactions(
        self, transactions: List[BitcoinTransaction]
    ) -> Dict[str, AddressCluster]:
        """Process transactions and compute common-input connected component clusters."""
        self.co_spend_graph.clear()
        self.address_to_cluster_id.clear()
        self.clusters.clear()

        # Step 1: Add co-spending edges for multi-input transactions
        for tx in transactions:
            inputs = [vin.address for vin in tx.inputs if vin.address]
            if len(inputs) > 1:
                # Add edges connecting all co-spending addresses
                for i in range(len(inputs) - 1):
                    self.co_spend_graph.add_edge(
                        inputs[i],
                        inputs[i + 1],
                        txid=tx.txid,
                    )
            elif len(inputs) == 1:
                self.co_spend_graph.add_node(inputs[0])

        # Step 2: Compute connected components
        components = list(nx.connected_components(self.co_spend_graph))
        
        # Sort components by size descending for deterministic cluster IDs
        components.sort(key=len, reverse=True)

        for idx, comp in enumerate(components):
            cluster_id = f"CLUSTER_{idx+1:04d}"
            cluster = AddressCluster(
                cluster_id=cluster_id,
                addresses=set(comp),
                entity_type="HEURISTIC_CLUSTER",
                confidence=0.85 if len(comp) > 1 else 1.0,
            )
            self.clusters[cluster_id] = cluster
            for addr in comp:
                self.address_to_cluster_id[addr] = cluster_id

        logger.info(f"Clustered {len(self.address_to_cluster_id)} addresses into {len(self.clusters)} clusters.")
        return self.clusters

    def get_cluster_for_address(self, address: str) -> Optional[AddressCluster]:
        """Look up the cluster containing a given address."""
        cluster_id = self.address_to_cluster_id.get(address)
        if cluster_id:
            return self.clusters.get(cluster_id)
        return None

    def get_cluster_id(self, address: str) -> Optional[str]:
        """Get the cluster ID string for an address."""
        return self.address_to_cluster_id.get(address)

    def get_cluster_members(self, cluster_id: str) -> Set[str]:
        """Return the set of addresses belonging to a cluster."""
        cluster = self.clusters.get(cluster_id)
        return cluster.addresses if cluster else set()

    def get_all_clusters_summary(self) -> List[Dict[str, Any]]:
        """Return structured summary list of all clusters."""
        return [c.to_dict() for c in self.clusters.values()]
