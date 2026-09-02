"""
Synthetic Forensic Dataset Generator.
Generates realistic Bitcoin transaction datasets with labeled forensic typologies:
Normal P2P, High Fan-In, High Fan-Out, Rapid Movement, Peel Chains, Dormant Activation,
Mixing-Like Structures, High-Value Transfers, Exchange Batching, and Clustered Identities.
"""

import os
import json
from datetime import datetime, timedelta
import pandas as pd


def generate_forensic_sample_dataset() -> pd.DataFrame:
    """Generate a rich, multi-pattern synthetic Bitcoin forensic dataset."""
    records = []
    base_time = datetime(2026, 1, 15, 10, 0, 0)

    # 1. Normal P2P Transactions (1-to-2 standard transfers)
    for i in range(1, 6):
        t = base_time + timedelta(hours=i * 2)
        records.append({
            "txid": f"tx_normal_{i:04d}_" + "a" * 48,
            "timestamp": t.isoformat(),
            "input_addresses": [f"1NormUser{i}MainnetAddress111111111111"],
            "output_addresses": [
                f"1Merchant{i}StoreAddress222222222222",
                f"1NormUser{i}ChangeAddress33333333333",
            ],
            "input_amounts": [1.50],
            "output_amounts": [0.45, 1.0498],
            "fee": 0.0002,
            "pattern_type": "NORMAL_P2P",
        })

    # 2. High Fan-In (Consolidation: 10 inputs -> 1 output)
    t_fanin = base_time + timedelta(days=1, hours=4)
    fanin_inputs = [f"1ConsolSource{j:02d}Addr11111111111111" for j in range(1, 11)]
    fanin_amounts = [0.25] * 10
    records.append({
        "txid": "tx_fanin_consolidation_0001_" + "b" * 40,
        "timestamp": t_fanin.isoformat(),
        "input_addresses": fanin_inputs,
        "output_addresses": ["1ConsolidationMasterVault9999999999"],
        "input_amounts": fanin_amounts,
        "output_amounts": [2.499],
        "fee": 0.001,
        "pattern_type": "HIGH_FAN_IN",
    })

    # 3. High Fan-Out (Dispersion: 1 input -> 15 outputs)
    t_fanout = base_time + timedelta(days=1, hours=8)
    fanout_outputs = [f"1DispersionTarget{k:02d}Addr222222222222" for k in range(1, 16)]
    fanout_amounts = [0.15] * 15
    records.append({
        "txid": "tx_fanout_dispersion_0001_" + "c" * 42,
        "timestamp": t_fanout.isoformat(),
        "input_addresses": ["1DispersionSourceVault88888888888"],
        "output_addresses": fanout_outputs,
        "input_amounts": [2.255],
        "output_amounts": fanout_amounts,
        "fee": 0.005,
        "pattern_type": "HIGH_FAN_OUT",
    })

    # 4. Rapid Movement / High Velocity (Funds relayed through 5 hops in 10 minutes)
    curr_addr = "1RapidRelayStartAddr000000000000"
    curr_amt = 5.00
    t_rapid = base_time + timedelta(days=2, hours=1)
    for hop in range(1, 6):
        next_addr = f"1RapidRelayHop{hop:02d}Addr33333333333333"
        t_hop = t_rapid + timedelta(minutes=hop * 2)
        records.append({
            "txid": f"tx_rapid_hop_{hop:02d}_" + "d" * 48,
            "timestamp": t_hop.isoformat(),
            "input_addresses": [curr_addr],
            "output_addresses": [next_addr],
            "input_amounts": [curr_amt],
            "output_amounts": [curr_amt - 0.0005],
            "fee": 0.0005,
            "pattern_type": "RAPID_MOVEMENT",
        })
        curr_addr = next_addr
        curr_amt -= 0.0005

    # 5. Peel Chain (5 consecutive peeling transactions)
    peel_addr = "1PeelChainOriginAddr111111111111"
    peel_balance = 20.0
    t_peel = base_time + timedelta(days=3, hours=2)
    for p in range(1, 6):
        peel_payment_addr = f"1PeelPaymentDest{p:02d}Addr44444444444"
        peel_next_change = f"1PeelChangeHop{p:02d}Addr555555555555"
        payment_amt = 0.50
        change_amt = peel_balance - payment_amt - 0.0003
        t_pstep = t_peel + timedelta(hours=p * 3)
        records.append({
            "txid": f"tx_peel_chain_step_{p:02d}_" + "e" * 44,
            "timestamp": t_pstep.isoformat(),
            "input_addresses": [peel_addr],
            "output_addresses": [peel_payment_addr, peel_next_change],
            "input_amounts": [peel_balance],
            "output_amounts": [payment_amt, change_amt],
            "fee": 0.0003,
            "pattern_type": "PEEL_CHAIN",
        })
        peel_addr = peel_next_change
        peel_balance = change_amt

    # 6. Mixing-like Transaction (CoinJoin-style: 5 inputs, 5 equal 0.1 BTC outputs)
    t_mix = base_time + timedelta(days=4, hours=6)
    mix_inputs = [f"1MixParticipant{m:02d}InAddr666666666666" for m in range(1, 6)]
    mix_outputs = [f"1MixAnonymized{m:02d}OutAddr77777777777" for m in range(1, 6)]
    records.append({
        "txid": "tx_coinjoin_mixing_structure_0001_" + "f" * 34,
        "timestamp": t_mix.isoformat(),
        "input_addresses": mix_inputs,
        "output_addresses": mix_outputs,
        "input_amounts": [0.1002] * 5,
        "output_amounts": [0.1000] * 5,
        "fee": 0.0010,
        "pattern_type": "MIXING_LIKE_STRUCTURE",
    })

    # 7. Dormant Address Activation (Old funding, 200 days dormancy, sudden large spend)
    t_dormant_old = base_time - timedelta(days=220)
    t_dormant_act = base_time + timedelta(days=5, hours=3)
    records.append({
        "txid": "tx_dormant_initial_funding_0001_" + "1" * 38,
        "timestamp": t_dormant_old.isoformat(),
        "input_addresses": ["1OldMinerFundingPool00000000000000"],
        "output_addresses": ["1DormantWhaleColdWalletAddr8888888"],
        "input_amounts": [50.0],
        "output_amounts": [49.999],
        "fee": 0.001,
        "pattern_type": "DORMANT_FUNDING",
    })
    records.append({
        "txid": "tx_dormant_sudden_activation_0002_" + "2" * 37,
        "timestamp": t_dormant_act.isoformat(),
        "input_addresses": ["1DormantWhaleColdWalletAddr8888888"],
        "output_addresses": [
            "1SuddenRecipientOffshoreVault99999",
            "1DormantWhaleResidualChange0000000",
        ],
        "input_amounts": [49.999],
        "output_amounts": [40.0, 9.998],
        "fee": 0.001,
        "pattern_type": "DORMANT_ACTIVATION",
    })

    # 8. Clustered Multi-Input Entity (3 input addresses in 1 tx -> forms 1 entity cluster)
    t_cluster = base_time + timedelta(days=6, hours=1)
    records.append({
        "txid": "tx_entity_cluster_co_spend_0001_" + "3" * 38,
        "timestamp": t_cluster.isoformat(),
        "input_addresses": [
            "1ClusterA_HotWalletAddr1111111111111",
            "1ClusterA_DesktopClientAddr222222222",
            "1ClusterA_MobileWalletAddr3333333333",
        ],
        "output_addresses": ["1ExchangeDepositBinanceGateway99999"],
        "input_amounts": [1.2, 0.8, 0.5],
        "output_amounts": [2.499],
        "fee": 0.001,
        "pattern_type": "COMMON_INPUT_CLUSTER",
    })

    return pd.DataFrame(records)


def save_sample_datasets(out_dir: str = "data/sample"):
    """Generate and write CSV, JSON, and JSONL sample datasets."""
    os.makedirs(out_dir, exist_ok=True)
    df = generate_forensic_sample_dataset()

    csv_path = os.path.join(out_dir, "transactions.csv")
    json_path = os.path.join(out_dir, "transactions.json")
    jsonl_path = os.path.join(out_dir, "transactions.jsonl")

    # Save CSV
    df.to_csv(csv_path, index=False)

    # Save JSON
    records = df.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # Save JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    # Save README
    readme_path = os.path.join(out_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("""# CryptoTrace AI Synthetic Forensic Datasets

This directory contains realistic, synthetic Bitcoin transaction datasets for offline forensic testing, benchmark validation, and demonstration.

## Files
- `transactions.csv`: Tabular format with JSON-encoded address and amount lists.
- `transactions.json`: Standard JSON array of transaction objects.
- `transactions.jsonl`: Line-delimited JSON format for streaming ingestion.

## Synthetic Typologies Included
1. **Normal P2P**: 1-input to 2-output standard payments with change.
2. **High Fan-In**: 10-input consolidation into a single master vault.
3. **High Fan-Out**: 1-input dispersion across 15 target addresses.
4. **Rapid Movement**: Funds relayed across 5 consecutive hops within 10 minutes (high velocity).
5. **Peel Chain**: 5 consecutive peeling steps (large payment + decaying change).
6. **Mixing-Like Structure**: CoinJoin-style 5-input, 5-output structure with equal amounts and high entropy.
7. **Dormant Activation**: Address inactive for >200 days with sudden 50 BTC transfer.
8. **Common-Input Cluster**: Multi-input spending linking 3 addresses to a single entity.

*All data is synthetic and non-attributable to real persons.*
""")

    print(f"Sample datasets generated in {out_dir}: {len(df)} transactions.")


if __name__ == "__main__":
    save_sample_datasets()
