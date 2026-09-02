"""
Unit tests for Graph construction and analytics.
"""

import pandas as pd
from src.cryptotrace.graph.builder import ForensicGraphBuilder
from src.cryptotrace.graph.analytics import GraphAnalytics


def test_graph_builder():
    df = pd.DataFrame(
        [
            {
                "txid": "TX_G01",
                "timestamp": "2026-01-01 12:00:00",
                "src_ip": "185.220.101.5",
                "src_country": "Netherlands",
                "src_asn": "AS13335",
                "input_addresses": ["W1"],
                "output_addresses": ["W2"],
                "input_amounts": [1.0],
                "output_amounts": [0.99],
                "fee": 0.01,
                "label": 1,
                "entity_type": "SUSPICIOUS_ACTOR",
            }
        ]
    )
    builder = ForensicGraphBuilder()
    G = builder.build_from_dataframe(df)

    assert "TX_G01" in G
    assert "W1" in G
    assert "185.220.101.5" in G

    analytics = GraphAnalytics(G)
    sub_G = analytics.extract_subgraph("TX_G01", hops=1)
    assert len(sub_G.nodes) >= 2
