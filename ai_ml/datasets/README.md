# 📊 Datasets for CryptoTrace AI

This directory contains the raw, processed, and sample datasets used for training, evaluation, and inference in the CryptoTrace AI machine learning pipeline.

## Dataset Overview

| Dataset | Source | Size | Features | Labels | Purpose |
|---------|--------|------|----------|--------|---------|
| **Elliptic** | Kaggle | ~204K transactions | 166 transaction features + graph | Licit/Illicit/Unknown | Supervised classification + Graph analysis |
| **BitcoinHeist** | UCI Archive | ~2.5M addresses | Topological address features | Ransomware families | Ransomware detection |

---

## 1. Elliptic Bitcoin Dataset

### Overview
The Elliptic dataset is a comprehensive labeling of Bitcoin transactions as either **licit**, **illicit**, or **unknown**. It includes a full transaction graph, making it ideal for both supervised learning and graph-based analysis.

### Dataset Statistics
- **Total Transactions**: 203,769
- **Total Transaction Edges**: 234,355 (graph connections)
- **Features per Transaction**: 166 (including aggregated network features)
- **Labeled Illicit**: 4,545 transactions (2.23%)
- **Labeled Licit**: 42,019 transactions (20.62%)
- **Unlabeled**: 157,205 transactions (77.15%)
- **Time Steps**: 49 weekly time periods
- **Imbalance Ratio**: 1:9.2 (illicit:licit)

### Official Source
- **URL**: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
- **Citation**: Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Barucca, P., Llull, M., & Minca, A. (2022). *Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics*. In NeurIPS FinCrime Workshop.
- **License**: CC0 1.0 Universal (Public Domain)

### Contents

```
datasets/raw/elliptic/
├── elliptic_txs_features.csv      # Transaction feature matrix (203,769 × 166)
├── elliptic_txs_edgelist.csv      # Transaction graph edges
├── elliptic_txs_classes.csv       # Transaction labels (licit/illicit/unknown)
└── elliptic_txs_mapping.csv       # (Optional) Additional transaction metadata
```

### File Descriptions

#### `elliptic_txs_features.csv`
- **Rows**: 203,769 (one per transaction)
- **Columns**: 166 features
  - Column 1: Transaction ID
  - Columns 2-166: Aggregate features from previous 1-49 week time steps
  - Features capture: degree, aggregated value, timing, etc.

#### `elliptic_txs_edgelist.csv`
- **Format**: `<source_tx_id>,<target_tx_id>`
- **Rows**: 234,355 (one per directed edge)
- Represents Bitcoin UTXO (Unspent Transaction Output) flow

#### `elliptic_txs_classes.csv`
- **Format**: `<transaction_id>,<class>`
- **Classes**: 
  - `1` = Illicit (4,545 transactions)
  - `2` = Licit (42,019 transactions)
  - `unknown` = Unknown label (157,205 transactions)

### Intended Use Cases
1. **Binary Classification**: Predict licit vs. illicit transactions
2. **Anomaly Detection**: Identify unusual transaction patterns
3. **Graph Neural Network Training**: Learn node embeddings from transaction flow
4. **Temporal Analysis**: Analyze transaction behavior over 49-week periods
5. **Investigation Prioritization**: Rank transactions by risk score

### Data Characteristics
- **Highly Imbalanced**: Illicit transactions are rare (2.23% of labeled data)
- **Temporally Ordered**: Transactions span 49 weekly time steps
- **Graph-Structured**: Full transaction relationship network
- **Aggregated Features**: Pre-aggregated network statistics reduce computation
- **Missing Labels**: 77% of transactions lack ground truth labels

### Download Instructions

#### Option 1: Kaggle CLI (Recommended)
```bash
# Install Kaggle CLI
pip install kaggle

# Configure credentials (download from https://www.kaggle.com/settings/account)
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download the dataset
kaggle datasets download -d ellipticco/elliptic-data-set -p ai_ml/datasets/raw/elliptic/

# Extract
unzip ai_ml/datasets/raw/elliptic/elliptic-data-set.zip -d ai_ml/datasets/raw/elliptic/
rm ai_ml/datasets/raw/elliptic/elliptic-data-set.zip
```

#### Option 2: Manual Download
1. Visit: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
2. Click "Download" button
3. Extract to: `ai_ml/datasets/raw/elliptic/`
4. Verify files: `elliptic_txs_features.csv`, `elliptic_txs_edgelist.csv`, `elliptic_txs_classes.csv`

#### Option 3: Automated Script
```bash
python scripts/download_datasets.py --dataset elliptic
```

### Data Leakage Prevention
⚠️ **CRITICAL**: This dataset contains temporal information (49 time steps).
- Use **time-aware train/validation/test splits** to prevent future information leakage
- Do NOT randomly shuffle time-dependent data
- Recommended split: 70% training, 10% validation, 20% test (by time)

### Validation Checklist
After downloading, verify:
```bash
python scripts/validate_datasets.py --dataset elliptic

Expected output:
✓ Files exist
✓ Row counts: features=203769, edges=234355, classes=203769
✓ No missing values (features may contain 0s, which is valid)
✓ No duplicates
✓ Class distribution: illicit=4545, licit=42019, unknown=157205
✓ Feature ranges valid
✓ Timestamps coherent
```

---

## 2. BitcoinHeist Ransomware Dataset

### Overview
BitcoinHeist is a Bitcoin address-level dataset focusing on ransomware-specific behavior. It contains topological features extracted from the Bitcoin blockchain and labels indicating ransomware family affiliations.

### Dataset Statistics
- **Total Bitcoin Addresses**: ~2.5 million
- **Labeled Ransomware Addresses**: ~2,000+
- **Feature Dimension**: 10-50 topological/behavioral features
- **Ransomware Families**: 80+ families
- **White-labeled (benign)**: Remaining addresses

### Official Source
- **Primary Source**: UCI Machine Learning Repository (https://archive.ics.uci.edu/)
- **Paper**: Bartoletti, M., Jourdan, S., Laporte, V., & Mattioli, L. (2020). *Tracing ransomware end-to-end*. IEEE S&P Security and Privacy.
- **License**: Open for research/education

### Contents
```
datasets/raw/bitcoinheist/
├── bitcoinheist_addresses.csv    # Bitcoin address features
├── bitcoinheist_labels.csv       # Address labels (ransomware family)
└── bitcoinheist_mapping.csv      # (Optional) Feature descriptions
```

### File Descriptions

#### `bitcoinheist_addresses.csv`
- **Rows**: ~2.5M (one per Bitcoin address)
- **Columns**: 10-50 topological/behavioral features
  - Degree (in/out)
  - Aggregated transaction value
  - Transaction count
  - Time-based features
  - Temporal patterns

#### `bitcoinheist_labels.csv`
- **Format**: `<address_id>,<family>`
- **Labels**: 
  - Ransomware family names (WhisperGate, REvil, Conti, etc.)
  - `benign` = Non-ransomware address

### Intended Use Cases
1. **Ransomware Detection**: Identify Bitcoin addresses involved in ransomware operations
2. **Family Classification**: Distinguish between ransomware families
3. **Behavioral Analysis**: Study ransomware-specific transaction patterns
4. **Supervised Learning**: Train classifiers on address-level features

### Download Instructions

#### Option 1: UCI Archive (Direct Download)
```bash
# Visit the UCI Archive page
# Download the dataset
# Extract to: ai_ml/datasets/raw/bitcoinheist/
```

#### Option 2: Automated Script
```bash
python scripts/download_datasets.py --dataset bitcoinheist
```

### Validation Checklist
```bash
python scripts/validate_datasets.py --dataset bitcoinheist

Expected output:
✓ Files exist
✓ Row counts valid
✓ No missing values
✓ Feature ranges valid
✓ Class distribution coherent
```

---

## 3. Dataset Directory Structure

```
ai_ml/datasets/
├── README.md                          # This file
├── .gitkeep                           # Git placeholder for empty directories
│
├── raw/                               # ⚠️ NOT committed to Git (too large)
│   ├── .gitkeep
│   ├── elliptic/
│   │   ├── elliptic_txs_features.csv
│   │   ├── elliptic_txs_edgelist.csv
│   │   └── elliptic_txs_classes.csv
│   │
│   └── bitcoinheist/
│       ├── bitcoinheist_addresses.csv
│       └── bitcoinheist_labels.csv
│
├── processed/                         # Preprocessed, normalized data
│   ├── .gitkeep
│   ├── elliptic/
│   │   ├── transactions_cleaned.csv
│   │   ├── features_normalized.csv
│   │   ├── graph_adjacency.npz
│   │   └── metadata.json
│   │
│   └── bitcoinheist/
│       ├── addresses_cleaned.csv
│       └── metadata.json
│
├── samples/                           # Small sample datasets for testing
│   ├── .gitkeep
│   ├── elliptic_sample_1000.csv      # 1,000 transaction sample
│   ├── bitcoinheist_sample_1000.csv  # 1,000 address sample
│   └── README.md                      # Sample documentation
│
└── synthetics/                        # Synthetic data for testing (optional)
    ├── .gitkeep
    └── README.md                      # Synthetic data documentation
```

---

## 4. Git Configuration

### .gitignore entries

Add to the repository's `.gitignore`:

```
# Large dataset files (prevent accidental Git commits)
ai_ml/datasets/raw/**
!ai_ml/datasets/raw/.gitkeep
!ai_ml/datasets/raw/**/README.md

ai_ml/datasets/processed/**
!ai_ml/datasets/processed/.gitkeep
!ai_ml/datasets/processed/**/README.md

# Processed data
*.csv.gz
*.parquet
*.npz
```

This ensures:
- ✓ Large raw datasets are not committed
- ✓ Processed datasets are not committed
- ✓ Directory structure is preserved with `.gitkeep`
- ✓ Documentation remains in Git

---

## 5. Data Validation & Preprocessing

### Validation Report

Before training any model, run validation:

```bash
python ai_ml/scripts/validate_datasets.py --dataset elliptic
```

Expected output:
```
[Dataset Validation Report]
Dataset: elliptic
Timestamp: 2025-09-03 10:30:00

✓ Structural Checks
  - Files found: 3/3
  - Features shape: (203769, 166)
  - Edges shape: (234355, 2)
  - Classes shape: (203769,)

✓ Data Quality
  - Missing values: 0
  - Duplicates: 0
  - Invalid types: 0
  - Malformed IDs: 0

✓ Statistical Summary
  - Class distribution:
    - Illicit: 4545 (2.23%)
    - Licit: 42019 (20.62%)
    - Unknown: 157205 (77.15%)
  - Feature ranges:
    - Min: 0.0
    - Max: 999999.0
    - Mean: 1234.5
    - Std: 5678.9

✓ Graph Validation
  - Edge connectivity: Valid
  - Isolated nodes: 12345
  - Connected components: 5

✓ Temporal Analysis
  - Time steps: 49
  - Timeline coverage: 2013-01-01 to 2014-01-31

[All checks passed ✓]
Validation Duration: 2.34 seconds
```

### Preprocessing Steps

1. **Missing Value Handling**: Fill or drop invalid records
2. **Duplicate Removal**: Identify and remove duplicate transactions
3. **Feature Normalization**: Scale features to [0, 1] or standardize
4. **Graph Construction**: Build adjacency matrices for GNN training
5. **Train/Test Split**: Time-aware split to prevent data leakage
6. **Feature Alignment**: Ensure all features match model requirements

---

## 6. Licensing & Citation

### How to Cite CryptoTrace AI Datasets

```bibtex
@dataset{elliptic2022,
  title={Elliptic Data Set: Opening Up Machine Learning on the Blockchain},
  author={Weber, Mark and Domeniconi, Giacomo and Chen, James and others},
  year={2022},
  url={https://www.kaggle.com/datasets/ellipticco/elliptic-data-set},
  publisher={Kaggle}
}

@dataset{bitcoinheist2020,
  title={BitcoinHeist: Topological Data Analysis on Bitcoin Transactions},
  author={Bartoletti, Massimo and Jourdan, Sébastien and Laporte, Vincent},
  year={2020},
  url={https://archive.ics.uci.edu/},
  publisher={UCI Machine Learning Repository}
}
```

### License Information

| Dataset | License | Commercial Use | Modification |
|---------|---------|-----------------|---------------|
| Elliptic | CC0 1.0 (Public Domain) | ✓ Yes | ✓ Yes |
| BitcoinHeist | UCI Open Access | ✓ Yes (Research) | ✓ Yes |

---

## 7. FAQ & Troubleshooting

### Q: Why aren't the datasets in Git?
**A**: The Elliptic and BitcoinHeist datasets are large (~500MB+). Committing them would bloat the repository and slow down clones. Instead, developers download them locally following the instructions above.

### Q: How do I verify the datasets are correctly downloaded?
**A**: Run `python scripts/validate_datasets.py --dataset elliptic`. This performs comprehensive checks on integrity, structure, and content.

### Q: Can I use a subset of the data for testing?
**A**: Yes! Sample datasets (1,000 transactions/addresses) are included in `datasets/samples/`. These are small enough to commit and run quick experiments.

### Q: What if the Kaggle dataset moves or is unavailable?
**A**: The download script includes fallback mechanisms and documentation. If Kaggle is unavailable:
1. Download manually from the link provided
2. Extract to the expected directory
3. Run validation to confirm integrity

### Q: How do I know if there's data leakage in my train/test split?
**A**: The validation script checks for temporal leakage. For the Elliptic dataset, always split by time (week), not randomly.

---

## 8. Next Steps

1. **Download Datasets**: Run `python scripts/download_datasets.py`
2. **Validate Data**: Run `python scripts/validate_datasets.py`
3. **Preprocess**: Run `python scripts/preprocess.py`
4. **Train Models**: Run `python scripts/train.py`
5. **Evaluate**: Run `python scripts/evaluate.py`
6. **Predict**: Run `python scripts/predict.py`

For detailed instructions, see [AI/ML Pipeline Documentation](../README.md).

---

**Last Updated**: 2025-09-03  
**Maintainer**: CryptoTrace AI Engineering Team
