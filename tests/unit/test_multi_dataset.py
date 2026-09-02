"""
Unit tests for Elliptic, Elliptic++, BitcoinHeist, and NetworkBridge loaders.
"""
from src.cryptotrace.ingestion.elliptic import EllipticDatasetLoader
from src.cryptotrace.ingestion.ellipticpp import EllipticPlusPlusLoader
from src.cryptotrace.ingestion.bitcoinheist import BitcoinHeistLoader
from src.cryptotrace.ingestion.network_bridge import NetworkObservationBridge


def test_elliptic_loader():
    loader = EllipticDatasetLoader()
    df_merged, df_edges = loader.load()
    assert not df_merged.empty
    assert "txId" in df_merged.columns
    assert "label" in df_merged.columns
    assert "time_step" in df_merged.columns


def test_ellipticpp_loader():
    loader = EllipticPlusPlusLoader()
    data = loader.load()
    assert "transactions" in data
    assert "wallets" in data
    assert "addr_tx" in data


def test_bitcoinheist_loader():
    loader = BitcoinHeistLoader()
    df_heist = loader.load()
    assert not df_heist.empty
    assert "length" in df_heist.columns
    assert "weight" in df_heist.columns
    assert "is_ransomware" in df_heist.columns


def test_network_bridge():
    loader = EllipticDatasetLoader()
    df_merged, _ = loader.load()
    bridge = NetworkObservationBridge()
    enriched = bridge.bridge_elliptic_dataset(df_merged.head(10))
    assert "src_ip" in enriched.columns
    assert "src_country" in enriched.columns
    assert "src_asn" in enriched.columns
    assert "timestamp" in enriched.columns
