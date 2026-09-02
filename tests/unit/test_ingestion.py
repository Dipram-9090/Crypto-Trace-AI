"""
Unit tests for data ingestion parsers (CSV, JSON, XML).
"""

import pytest
import os
import tempfile
import json
from src.cryptotrace.ingestion import load_csv, load_json, load_xml


def test_csv_parser():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(
            "txid,timestamp,src_ip,dst_ip,src_port,dst_port,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,src_country,dst_country,src_asn,dst_asn,label,entity_type\n"
        )
        f.write(
            'TX_001,2026-01-01 12:00:00,185.220.101.5,51.15.89.2,54321,8333,"[""1BTC001""]","[""1BTC002""]","[1.5]","[1.49]","0.01",p2pkh,Netherlands,Germany,AS13335,AS24940,1,SUSPICIOUS_ACTOR\n'
        )
        temp_csv = f.name

    try:
        df, report = load_csv(temp_csv)
        assert len(df) == 1
        assert report.valid_rows == 1
        assert df.iloc[0]["txid"] == "TX_001"
    finally:
        os.remove(temp_csv)


def test_json_parser():
    records = [
        {
            "txid": "TX_J01",
            "timestamp": "2026-01-01 12:05:00",
            "input_addresses": ["W1"],
            "output_addresses": ["W2"],
            "input_amounts": [1.0],
            "output_amounts": [0.99],
            "fee": 0.01,
            "label": 0,
        }
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(records, f)
        temp_json = f.name

    try:
        df, report = load_json(temp_json)
        assert len(df) == 1
        assert df.iloc[0]["txid"] == "TX_J01"
    finally:
        os.remove(temp_json)
