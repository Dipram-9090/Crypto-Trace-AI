"""
Unit tests for Bitcoin protocol models, script classification, address validation, and RPC adapter.
"""

import pytest
from src.cryptotrace.blockchain.models import BitcoinTransaction, TxInput, TxOutput, BitcoinBlock
from src.cryptotrace.blockchain.bitcoin.scripts import (
    identify_script_type,
    parse_op_return_payload,
    disassemble_script_opcodes,
)
from src.cryptotrace.blockchain.addresses.validator import (
    is_valid_bitcoin_address,
    validate_base58_checksum,
    validate_bech32,
)
from src.cryptotrace.blockchain.addresses.classifier import (
    classify_address_encoding,
    inspect_address_details,
)
from src.cryptotrace.blockchain.rpc.bitcoin_core import BitcoinCoreRPC


def test_script_type_identification():
    # P2PKH
    p2pkh_hex = "76a91489abcdefabbaabbaabbaabbaabbaabbaabba88ac"
    assert identify_script_type(p2pkh_hex) == "p2pkh"

    # P2SH
    p2sh_hex = "a91489abcdefabbaabbaabbaabbaabbaabbaabba87"
    assert identify_script_type(p2sh_hex) == "p2sh"

    # P2WPKH
    p2wpkh_hex = "0014" + "ab" * 20
    assert identify_script_type(p2wpkh_hex) == "p2wpkh"

    # P2WSH
    p2wsh_hex = "0020" + "ab" * 32
    assert identify_script_type(p2wsh_hex) == "p2wsh"

    # P2TR
    p2tr_hex = "5120" + "ab" * 32
    assert identify_script_type(p2tr_hex) == "p2tr"

    # OP_RETURN
    op_ret = "6a0a48656c6c6f20425443"
    assert identify_script_type(op_ret) == "op_return"
    payload = parse_op_return_payload(op_ret)
    assert payload == "Hello BTC"


def test_script_disassembly():
    p2pkh_hex = "76a91489abcdefabbaabbaabbaabbaabbaabbaabba88ac"
    dis = disassemble_script_opcodes(p2pkh_hex)
    assert "OP_DUP" in dis and "OP_CHECKSIG" in dis


def test_address_validation_and_classification():
    # Valid P2PKH
    addr_legacy = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"
    assert is_valid_bitcoin_address(addr_legacy)
    assert classify_address_encoding(addr_legacy) == "P2PKH_LEGACY"

    # Valid P2SH
    addr_p2sh = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
    assert is_valid_bitcoin_address(addr_p2sh)
    assert classify_address_encoding(addr_p2sh) == "P2SH_SCRIPT"

    # Valid Native SegWit Bech32
    addr_segwit = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
    assert is_valid_bitcoin_address(addr_segwit)
    assert classify_address_encoding(addr_segwit) == "P2WPKH_SEGWIT"

    # Valid Taproot Bech32m
    addr_taproot = "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0"
    assert is_valid_bitcoin_address(addr_taproot)
    assert classify_address_encoding(addr_taproot) == "P2TR_TAPROOT"

    # Invalid address
    assert not is_valid_bitcoin_address("invalid_address_123")


def test_bitcoin_core_rpc_offline_safety():
    rpc = BitcoinCoreRPC(host="127.0.0.1", port=18332)
    assert not rpc.check_connection()
    assert rpc.get_raw_transaction("0" * 64) is None
