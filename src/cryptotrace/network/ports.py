"""
Network Port Classification and Protocol Mapping.
"""

def classify_port(port: int) -> str:
    """Classify network port into Bitcoin standard, RPC, ephemeral, or proxy."""
    if port == 8333 or port == 18333:
        return "BITCOIN_MAINNET_P2P"
    elif port == 8332 or port == 18332:
        return "BITCOIN_RPC"
    elif port == 9050 or port == 9150:
        return "TOR_SOCKS_PROXY"
    elif port == 4444 or port == 7656:
        return "I2P_PROXY"
    elif port > 1024:
        return "EPHEMERAL_SOURCE_PORT"
    else:
        return "PRIVILEGED_SYSTEM_PORT"
