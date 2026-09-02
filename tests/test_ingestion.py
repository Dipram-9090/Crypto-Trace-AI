"""
Unit tests for data ingestion parsers (CSV, JSON, XML).
"""
import pytest
import os
import tempfile
import json
import xml.etree.ElementTree as ET
from src.ingestion.csv_parser import parse_csv
from src.ingestion.json_parser import parse_json
from src.ingestion.xml_parser import parse_xml


def test_csv_parser():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("txid,timestamp,src_ip,dst_ip,src_port,dst_port,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,src_country,dst_country,src_asn,dst_asn,label,entity_type\n")
        f.write('TX_001,2026-01-01 12:00:00,185.220.101.5,51.15.89.2,54321,8333,"[""1BTC001""]","[""1BTC002""]","[1.5]","[1.49]","0.01",p2pkh,Netherlands,Germany,AS13335,AS24940,1,SUSPICIOUS_ACTOR\n')
        f.write('TX_001,2026-01-01 12:00:00,185.220.101.5,51.15.89.2,54321,8333,"[""1BTC001""]","[""1BTC002""]","[1.5]","[1.49]","0.01",p2pkh,Netherlands,Germany,AS13335,AS24940,1,SUSPICIOUS_ACTOR\n') # duplicate
        temp_csv = f.name

    try:
        df, report = parse_csv(temp_csv)
        assert len(df) == 1
        assert report.valid_rows == 1
        assert report.duplicate_rows == 1
        assert df.iloc[0]["txid"] == "TX_001"
        assert df.iloc[0]["label"] == 1
    finally:
        os.remove(temp_csv)


def test_json_parser():
    records = [
        {
            "txid": "TX_J01",
            "timestamp": "2026-01-01 12:05:00",
            "src_ip": "51.15.89.2",
            "dst_ip": "104.244.72.1",
            "src_port": 12345,
            "dst_port": 8333,
            "input_addresses": ["1BTC101"],
            "output_addresses": ["1BTC102"],
            "input_amounts": [2.0],
            "output_amounts": [1.99],
            "fee": 0.01,
            "script_type": "p2wpkh",
            "src_country": "Germany",
            "dst_country": "United States",
            "src_asn": "AS24940",
            "dst_asn": "AS16509",
            "label": 0,
            "entity_type": "NORMAL_USER"
        }
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(records, f)
        temp_json = f.name

    try:
        df, report = parse_json(temp_json)
        assert len(df) == 1
        assert report.valid_rows == 1
        assert df.iloc[0]["txid"] == "TX_J01"
    finally:
        os.remove(temp_json)


def test_xml_parser():
    xml_content = """
    <transactions>
        <transaction>
            <txid>TX_X01</txid>
            <timestamp>2026-01-01 12:10:00</timestamp>
            <src_ip>104.244.72.1</src_ip>
            <dst_ip>45.33.32.1</dst_ip>
            <src_port>8333</src_port>
            <dst_port>8333</dst_port>
            <input_addresses>["1BTC201"]</input_addresses>
            <output_addresses>["1BTC202"]</output_addresses>
            <input_amounts>[0.5]</input_amounts>
            <output_amounts>[0.495]</output_amounts>
            <fee>0.005</fee>
            <script_type>p2sh</script_type>
            <src_country>United States</src_country>
            <dst_country>Switzerland</dst_country>
            <src_asn>AS16509</src_asn>
            <dst_asn>AS51167</dst_asn>
            <label>0</label>
            <entity_type>MERCHANT</entity_type>
        </transaction>
    </transactions>
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content.strip())
        temp_xml = f.name

    try:
        df, report = parse_xml(temp_xml)
        assert len(df) == 1
        assert report.valid_rows == 1
        assert df.iloc[0]["txid"] == "TX_X01"
    finally:
        os.remove(temp_xml)
