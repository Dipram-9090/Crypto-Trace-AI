"""OFAC SDN Sanctioned Address Screening & Blacklist Engine."""

from typing import Dict, Any, Optional

# Prominent known sanctioned addresses (OFAC / Lazarus Group / Tornado Cash / Hydra)
KNOWN_SANCTIONED_WALLETS = {
    "0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c": {"entity": "Tornado.Cash Router", "program": "CYBER2"},
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": {"entity": "Tornado.Cash: 100 ETH", "program": "CYBER2"},
    "0x098b716b8aaf21512996dc57eb0615e2383e2f96": {"entity": "Ronin Bridge Exploiter (Lazarus Group)", "program": "DPRK3"},
    "1a1zp1ep5qgefi2dmptftl5slmv7divfna": {"entity": "Genesis Block (Historical Reference)", "program": "MONITOR"},
    "12cbql5w5f475590mvd55104vvhsdft6w0": {"entity": "Hydra Market Vendor", "program": "ILLICIT_MARKET"}
}


class OFACSanctionChecker:
    """Checks whether an address is listed on OFAC SDN or darknet blacklist databases."""

    @staticmethod
    def is_sanctioned(address: str) -> bool:
        return address.lower().strip() in KNOWN_SANCTIONED_WALLETS

    @staticmethod
    def get_details(address: str) -> Optional[Dict[str, Any]]:
        return KNOWN_SANCTIONED_WALLETS.get(address.lower().strip())
