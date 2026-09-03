# 🤖 AI/ML Pipeline — Complete Machine Learning System for CryptoTrace AI

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Quick Start](#quick-start)
4. [Datasets](#datasets)
5. [Pipeline Components](#pipeline-components)
6. [Models](#models)
7. [Risk Scoring](#risk-scoring)
8. [Backend API Integration](#backend-api-integration)
9. [Command Reference](#command-reference)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)
12. [Important Disclaimers](#important-disclaimers)

---

## Overview

The CryptoTrace AI machine learning pipeline provides:

✅ **Supervised Learning**: XGBoost, Random Forest classifiers for licit/illicit transaction detection  
✅ **Unsupervised Anomaly Detection**: Isolation Forest for novel transaction patterns  
✅ **Graph Neural Networks**: GraphSAGE for relational transaction embedding  
✅ **Explainability**: SHAP and LIME for feature attribution  
✅ **Risk Scoring**: Normalized 0-100 investigation priority scores  
✅ **Offline Capability**: Complete inference works without internet  
✅ **Reproducibility**: Full tracking of models, features, and configuration  
✅ **Enterprise-Grade**: Production-quality validation, error handling, and logging  

### Key Design Principles

1. **Risk vs. Guilt**: Scores indicate investigation priority, NOT criminality
2. **Explainability**: Every prediction includes top features and investigation signals
3. **Human-in-the-Loop**: Final determination always belongs to the investigator
4. **No Silent Failures**: Comprehensive validation and error reporting
5. **Offline First**: Works completely offline after model initialization

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRYPTOTRACE AI ML PIPELINE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT DATA                                                       │
│  ├─ Elliptic Bitcoin Dataset (203K transactions)                 │
│  ├─ BitcoinHeist Ransomware Dataset (2.5M addresses)             │
│  └─ Custom Transaction Data (CSV/JSON)                           │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ DATA LAYER                                                 │  │
│  ├─ Data Loading (Chunked reading, streaming)                 │  │
│  ├─ Validation (Integrity, structure, quality checks)         │  │
│  └─ Preprocessing (Cleaning, normalization, feature eng.)    │  │
│  └─ Time-Aware Splitting (Prevent temporal leakage)           │  │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ FEATURE ENGINEERING LAYER                                  │  │
│  ├─ Transaction Features                                       │  │
│  │   • Aggregation (volume, count, frequency)                  │  │
│  │   • Temporal (burst, velocity, time patterns)               │  │
│  │   • Behavioral (mixing, consolidation, fund flow)           │  │
│  ├─ Graph Features                                             │  │
│  │   • Topological (degree, centrality, clustering)            │  │
│  │   • Structural (components, paths, motifs)                  │  │
│  └─ Derived Features                                            │  │
│      • Normalized and scaled vectors                            │  │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ MODEL LAYER (Ensemble)                                     │  │
│  │                                                             │  │
│  │  Model A: Isolation Forest                                 │  │
│  │  ├─ Anomaly Score: [0, 1]                                  │  │
│  │  └─ Use: Unsupervised detection                            │  │
│  │                                                             │  │
│  │  Model B: Random Forest / XGBoost                          │  │
│  │  ├─ Probability: [0, 1]                                    │  │
│  │  └─ Use: Supervised classification                         │  │
│  │                                                             │  │
│  │  Model C: Graph Neural Network                             │  │
│  │  ├─ Node Embedding: [0, 1]                                 │  │
│  │  └─ Use: Relational patterns                               │  │
│  │                                                             │  │
│  └─ Ensemble Voting: Weighted average of model outputs        │  │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ RISK SCORING LAYER                                         │  │
│  ├─ Normalize to [0, 100]                                      │  │
│  ├─ Map to Risk Levels                                        │  │
│  │   • LOW (0-20): Routine monitoring                         │  │
│  │   • MODERATE (21-40): Standard review                      │  │
│  │   • ELEVATED (41-60): Heightened review                    │  │
│  │   • HIGH (61-80): Urgent investigation                     │  │
│  │   • CRITICAL (81-100): Immediate action                    │  │
│  └─ Explainability: Top features + investigation signals      │  │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ EXPLAINABILITY LAYER                                       │  │
│  ├─ Feature Importance (SHAP, LIME)                           │  │
│  ├─ Investigation Signals                                      │  │
│  │   • "High transaction velocity"                            │  │
│  │   • "Rapid fund mixing detected"                           │  │
│  │   • "Unusual counterparty patterns"                         │  │
│  ├─ Graph Inspection                                           │  │
│  └─ Human-Readable Justifications                              │  │
│                         ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ API LAYER                                                  │  │
│  ├─ POST /api/ml/analyze                                      │  │
│  ├─ GET /api/ml/models                                        │  │
│  ├─ GET /api/ml/health                                        │  │
│  └─ Webhook support for batch processing                      │  │
│                         ↓                                         │
│  OUTPUT: Risk Scores & Investigation Leads                       │
│  └─ Frontend Dashboard                                           │
│  └─ Investigation Tools                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Download Datasets

```bash
# Download all datasets
python scripts/download_datasets.py --dataset all

# Or individual datasets
python scripts/download_datasets.py --dataset elliptic
python scripts/download_datasets.py --dataset bitcoinheist
```

### 2. Validate Data

```bash
python scripts/validate_datasets.py --dataset all
```

### 3. Preprocess Data

```bash
python scripts/preprocess.py --dataset elliptic --output data/processed/
```

### 4. Train Models

```bash
# Train isolation forest (unsupervised)
python scripts/train.py --model isolation_forest --dataset elliptic

# Train random forest (supervised)
python scripts/train.py --model random_forest --dataset elliptic

# Train XGBoost (supervised)
python scripts/train.py --model xgboost --dataset elliptic

# Train GNN
python scripts/train.py --model gnn --dataset elliptic
```

### 5. Evaluate Models

```bash
python scripts/evaluate.py --model elliptic_random_forest --dataset elliptic
```

### 6. Run Inference

```bash
# Single file inference
python scripts/predict.py --input data/transactions.csv --model ensemble

# Batch inference
python scripts/predict.py --input data/ --model ensemble --batch-size 10000

# Output: CSV with risk scores, JSON with top leads
```

### 7. Integration Testing

```bash
pytest ai_ml/tests/test_ml_pipeline.py -v
```

---

## Datasets

### Elliptic Bitcoin Dataset

- **Size**: 203,769 transactions, 234,355 edges
- **Features**: 166 transaction features
- **Labels**: 4,545 illicit, 42,019 licit, 157,205 unknown
- **Usage**: Supervised classification + graph analysis

**Download**:
```bash
python scripts/download_datasets.py --dataset elliptic
```

### BitcoinHeist Ransomware Dataset

- **Size**: ~2.5M Bitcoin addresses
- **Features**: Topological address metrics
- **Labels**: Ransomware families
- **Usage**: Ransomware-specific detection

**Download**:
```bash
python scripts/download_datasets.py --dataset bitcoinheist
```

### Sample Datasets

For quick testing without downloading full datasets:

```bash
python scripts/train.py --dataset elliptic --use-sample
```

---

## Pipeline Components

### Data Layer

**Location**: `ai_ml/src/data/`

#### Loaders (`loaders.py`)
- `EllipticDataLoader`: Load Elliptic dataset
- `BitcoinHeistDataLoader`: Load BitcoinHeist dataset
- `DataLoaderFactory`: Factory for dataset selection
- Memory-efficient chunked reading for large datasets

**Usage**:
```python
from ai_ml.src.data.loaders import DataLoaderFactory

loader = DataLoaderFactory.create_loader("elliptic")
features, edgelist, classes = loader.load_full_dataset()
```

#### Validators (`validators.py`)
- `EllipticValidator`: Validate Elliptic integrity
- `BitcoinHeistValidator`: Validate BitcoinHeist integrity
- Structural checks (files, shapes)
- Data quality checks (missing values, duplicates)
- Statistical validation
- Graph validation

**Usage**:
```python
from ai_ml.src.data.validators import EllipticValidator

validator = EllipticValidator()
validator.validate()
```

### Feature Engineering Layer

**Location**: `ai_ml/src/data/` and existing modules

#### Transaction Features
- **Aggregation**: volume, count, frequency
- **Temporal**: burst, velocity, patterns
- **Behavioral**: mixing, consolidation, flow

#### Graph Features
- **Topological**: degree, centrality, clustering
- **Structural**: components, paths
- **Temporal**: time-aware propagation

### Model Layer

**Location**: `ai_ml/src/models/`

#### Model A: Isolation Forest
- Unsupervised anomaly detection
- Outlier isolation in feature space
- Output: Anomaly score [0, 1]

#### Model B: Random Forest / XGBoost
- Supervised binary classification
- Handles class imbalance with weighted loss
- Output: Probability [0, 1]

#### Model C: Graph Neural Network
- GraphSAGE for node embedding
- Transaction relationship modeling
- Output: Embedding + prediction

#### Ensemble
- Weighted voting of model outputs
- Configurable weights per model
- Aggregated confidence score

### Risk Scoring Layer

**Location**: `ai_ml/src/inference/risk_scoring.py`

Converts model outputs to normalized risk scores:

```
Anomaly Score [0, 1] → Risk Score [0, 100] → Risk Level
                            ↓
                    (LOW/MODERATE/ELEVATED/HIGH/CRITICAL)
```

**Usage**:
```python
from ai_ml.src.inference.risk_scoring import RiskScorer, RiskLevel

scorer = RiskScorer()

# From anomaly detection
risk_score = scorer.score_from_anomaly(anomaly_score=0.75)

# From classifier
risk_score = scorer.score_from_probability(probability=0.85)

# From ensemble
risk_score = scorer.score_from_ensemble([75, 82, 70])

# Get level
level = scorer.get_risk_level(risk_score)  # Returns RiskLevel enum
```

### Explainability Layer

**Location**: Existing SHAP/LIME modules

- SHAP: Game-theoretic feature importance
- LIME: Local interpretable model-agnostic explanations
- Investigation signals: Human-readable justifications
- Graph explanations: Sub-graph extraction

**Usage**:
```python
from ai_ml.src.inference.risk_scoring import InvestigationSignalGenerator

signals = InvestigationSignalGenerator.generate_signals_from_features(
    top_features=[("transaction_velocity", 0.34), ...],
    risk_score=82
)
```

### Model Registry

**Location**: `ai_ml/src/models/model_registry.py`

Manages trained models and metadata:

```python
from ai_ml.src.models.model_registry import ModelRegistry, ModelMetadata

# Initialize registry
registry = ModelRegistry("ai_ml/models")

# Save model with metadata
metadata = ModelMetadata(
    model_name="elliptic_ensemble",
    version="1.0.0",
    model_type="ensemble",
    training_dataset="elliptic",
    feature_list=[...],
    random_seed=42
)
registry.save_model(model, "elliptic_ensemble", metadata)

# Load model
model, metadata = registry.load_model("elliptic_ensemble")

# List models
models = registry.list_models()
```

### Evaluation Metrics

**Location**: `ai_ml/src/evaluation/metrics.py`

Comprehensive metric computation:

```python
from ai_ml.src.evaluation.metrics import ClassificationMetrics

metrics = ClassificationMetrics(y_true, y_pred, y_pred_proba)
print(f"Precision: {metrics.metrics['precision']:.4f}")
print(f"Recall: {metrics.metrics['recall']:.4f}")
print(f"F1: {metrics.metrics['f1']:.4f}")
print(f"ROC-AUC: {metrics.metrics['roc_auc']:.4f}")
print(f"PR-AUC: {metrics.metrics['pr_auc']:.4f}")
```

---

## Models

### Model Specifications

| Model | Type | Input | Output | Use Case |
|-------|------|-------|--------|----------|
| **Isolation Forest** | Unsupervised | Features | Anomaly [0,1] | Novel patterns |
| **Random Forest** | Supervised | Features | Probability [0,1] | Baseline classifier |
| **XGBoost** | Supervised | Features | Probability [0,1] | Best accuracy |
| **GraphSAGE** | Graph NN | Features + Graph | Embedding | Relational patterns |
| **Ensemble** | Meta | Model outputs | Risk Score [0,100] | Final decision |

### Model Training

#### Time-Aware Train/Test Split

**CRITICAL**: The Elliptic dataset contains temporal information.

```python
# CORRECT: Time-based split (prevents data leakage)
train_data = data[data['timestamp'] <= cutoff_date]
test_data = data[data['timestamp'] > cutoff_date]

# WRONG: Random split (allows future information leakage)
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
```

#### Class Imbalance Handling

The Elliptic dataset is highly imbalanced:
- Illicit: 4,545 (2.23%)
- Licit: 42,019 (20.62%)
- Unknown: 157,205 (77.15%)

**Strategies**:
1. **Class Weights**: Scale loss by class frequency
2. **Balanced Sampling**: Oversampling minorities in mini-batches
3. **Threshold Tuning**: Adjust decision boundary
4. **Ensemble**: Combine multiple approaches

### Model Evaluation

```bash
python scripts/evaluate.py --model elliptic_xgboost --dataset elliptic
```

Expected Output:
```
Classification Metrics:
  Precision: 0.9247
  Recall: 0.8753
  F1 Score: 0.8992
  ROC-AUC: 0.9847
  PR-AUC: 0.9542

Confusion Matrix:
  TN=9876, FP=123
  FN=45, TP=956
```

---

## Risk Scoring

### Scoring Algorithm

```
1. Normalize model output to [0, 1]
   - Anomaly score: Already [0, 1]
   - Probability: Already [0, 1]
   - Raw score: Sigmoid/Min-Max scaling

2. Convert to [0, 100] risk scale
   risk_score = normalized_output * 100

3. Map to risk level
   Level = {
     0-20: LOW (routine monitoring),
     21-40: MODERATE (standard review),
     41-60: ELEVATED (heightened review),
     61-80: HIGH (urgent investigation),
     81-100: CRITICAL (immediate action)
   }

4. Generate investigation signals
   signals = extract_feature_importance(model, transaction)
```

### Risk Levels

| Level | Score | Investigation Priority | Action |
|-------|-------|----------------------|--------|
| **LOW** | 0-20 | Routine | Queue for batch review |
| **MODERATE** | 21-40 | Standard | Include in standard review |
| **ELEVATED** | 41-60 | Heightened | Priority review |
| **HIGH** | 61-80 | Urgent | Immediate investigator review |
| **CRITICAL** | 81-100 | Immediate | Escalate + immediate action |

### Example Risk Score Result

```python
{
  "entity_id": "TX123456",
  "risk_score": 82,
  "risk_level": "HIGH",
  "anomaly_score": 0.78,
  "classification_probability": 0.85,
  "model_version": "ensemble_v1.0",
  "top_features": [
    "fund_dispersion",
    "transaction_velocity",
    "counterparty_count"
  ],
  "investigation_signals": [
    "High transaction velocity detected",
    "Unusual fund dispersion pattern",
    "High network centrality"
  ],
  "confidence": 0.92,
  "disclaimer": "Risk score indicates investigation priority and does not establish criminality or identify a person."
}
```

---

## Backend API Integration

### REST Endpoints

#### POST /api/ml/analyze

Analyze transactions and return risk scores.

**Request**:
```json
{
  "dataset_path": "data/transactions.csv",
  "model_name": "ensemble",
  "include_explanations": true
}
```

**Response**:
```json
{
  "status": "success",
  "records_analyzed": 10000,
  "high_risk_count": 73,
  "moderate_risk_count": 245,
  "low_risk_count": 9682,
  "average_risk_score": 28.5,
  "results": [
    {
      "entity_id": "TX123456",
      "risk_score": 82,
      "risk_level": "HIGH",
      "investigation_signals": [...]
    },
    ...
  ],
  "timestamp": "2024-09-03T10:30:00Z"
}
```

#### GET /api/ml/models

List available models.

**Response**:
```json
[
  {
    "model_name": "elliptic_ensemble",
    "model_type": "ensemble",
    "version": "1.0.0",
    "training_dataset": "elliptic",
    "evaluation_metrics": {
      "precision": 0.92,
      "recall": 0.87,
      "f1": 0.89,
      "roc_auc": 0.98
    },
    "feature_count": 166,
    "training_date": "2024-01-01T10:00:00Z"
  }
]
```

#### GET /api/ml/health

Health check.

**Response**:
```json
{
  "status": "healthy",
  "models_available": 4,
  "timestamp": "2024-09-03T10:30:00Z"
}
```

### FastAPI Integration

Add to `backend/main.py`:

```python
from ai_ml.src.models.model_registry import ModelRegistry
from ai_ml.src.api.ml_service import MLServiceHandler, AnalysisRequest, AnalysisResponse

# Initialize
registry = ModelRegistry()
ml_handler = MLServiceHandler(registry)

@app.post("/api/ml/analyze", response_model=AnalysisResponse)
async def analyze_transactions(request: AnalysisRequest):
    return await ml_handler.analyze_transactions(request)

@app.get("/api/ml/models")
async def list_models():
    return ml_handler.get_available_models()

@app.get("/api/ml/health")
async def health_check():
    return ml_handler.health_check()
```

---

## Command Reference

### Download Datasets

```bash
# All datasets
python scripts/download_datasets.py --dataset all

# Specific dataset
python scripts/download_datasets.py --dataset elliptic
python scripts/download_datasets.py --dataset bitcoinheist

# Custom output directory
python scripts/download_datasets.py --dataset elliptic --output /custom/path
```

### Validate Data

```bash
# Validate all
python scripts/validate_datasets.py --dataset all

# Validate specific
python scripts/validate_datasets.py --dataset elliptic

# Custom data directory
python scripts/validate_datasets.py --dataset elliptic --data-dir /custom/path
```

### Preprocessing

```bash
# Full preprocessing
python scripts/preprocess.py --dataset elliptic --output data/processed/

# With sample
python scripts/preprocess.py --dataset elliptic --sample 1000

# Specific split
python scripts/preprocess.py --dataset elliptic --train-ratio 0.7
```

### Training

```bash
# Train single model
python scripts/train.py --model random_forest --dataset elliptic

# Options
python scripts/train.py \
  --model xgboost \
  --dataset elliptic \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.01 \
  --output models/

# Train ensemble (all models)
python scripts/train.py --model ensemble --dataset elliptic
```

### Evaluation

```bash
# Evaluate model
python scripts/evaluate.py --model elliptic_random_forest --dataset elliptic

# Compare models
python scripts/evaluate.py --compare all --dataset elliptic

# Save report
python scripts/evaluate.py --model elliptic_xgboost --output reports/eval.json
```

### Inference

```bash
# Single file
python scripts/predict.py --input data/transactions.csv --model ensemble

# Batch processing
python scripts/predict.py --input data/ --model ensemble --batch-size 10000

# Output format
python scripts/predict.py --input data/tx.csv --model ensemble --format json

# Save results
python scripts/predict.py --input data/tx.csv --model ensemble --output reports/
```

---

## Testing

### Run Tests

```bash
# All tests
pytest ai_ml/tests/ -v

# Specific test class
pytest ai_ml/tests/test_ml_pipeline.py::TestRiskScorer -v

# With coverage
pytest ai_ml/tests/ --cov=ai_ml --cov-report=html

# Specific tests only
pytest ai_ml/tests/test_ml_pipeline.py::TestRiskScorer::test_score_from_anomaly_linear -v
```

### Test Coverage

The test suite includes:
- ✅ Data loading and validation
- ✅ Risk scoring algorithms
- ✅ Model registry operations
- ✅ Evaluation metrics
- ✅ API integration
- ✅ Edge cases and error handling

---

## Troubleshooting

### Issue: Kaggle Dataset Download Fails

**Solution**:
```bash
# Configure Kaggle CLI
mkdir ~/.kaggle
cp /path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Verify
kaggle datasets download -d ellipticco/elliptic-data-set -p temp/
```

### Issue: Out of Memory When Loading Dataset

**Solution**: Use chunked reading:
```python
from ai_ml.src.data.loaders import EllipticDataLoader

loader = EllipticDataLoader()
for chunk in loader.load_features(chunk_size=10000):
    # Process chunk
    pass
```

### Issue: Model Predictions Vary Between Runs

**Solution**: Set random seeds:
```python
import numpy as np
import random
import torch

np.random.seed(42)
random.seed(42)
torch.manual_seed(42)
```

### Issue: Data Leakage Warning

**Solution**: Use time-aware splits for Elliptic:
```python
cutoff = data['timestamp'].quantile(0.7)
train = data[data['timestamp'] <= cutoff]
test = data[data['timestamp'] > cutoff]
```

---

## Important Disclaimers

### ⚠️ What This System Does NOT Do

❌ **Does NOT**:
- Establish criminality or guilt
- Identify specific individuals
- Make final determinations
- Provide legal conclusions
- Replace human judgment

### ✅ What This System DOES Do

✅ **Does**:
- Indicate investigation priority
- Flag anomalous transactions
- Provide analytical risk indicators
- Support investigator decisions
- Generate explainable leads

### Legal & Ethical Statement

> **CryptoTrace AI provides analytical risk indicators and investigation leads. It does not identify individuals, establish criminality, or make definitive determinations. All final decisions rest with qualified human investigators.**

### Model Limitations

1. **Training Data Bias**: Models are trained on available labeled data
2. **Temporal Shifts**: Illicit patterns change over time
3. **False Positives**: Anomalies ≠ Criminality
4. **False Negatives**: Sophisticated schemes may evade detection
5. **Data Gaps**: Unknown-labeled transactions limit training signal

### Recommended Practices

1. Use as ONE tool among many
2. Combine with domain expertise
3. Verify findings through investigation
4. Consider false positive costs
5. Regularly retrain on new data
6. Monitor model drift
7. Document all assumptions
8. Maintain audit trails
9. Have human review before action
10. Consider false positive/negative tradeoffs

---

## Architecture Highlights

### Reproducibility

Every model includes:
- Training dataset version/hash
- Feature list
- Hyperparameters
- Random seed
- Training date
- Evaluation metrics

### Offline-First Design

After initial setup:
1. Download datasets → Local storage
2. Train models → Local weights
3. All inference runs locally
4. No internet required for inference
5. Optional cloud sync for collaboration

### Scalability

- Chunked data loading (handles GB datasets)
- Batch inference (process millions of transactions)
- Distributed training ready (PyTorch + Horovod)
- Database backend option (PostgreSQL)
- Caching/Redis support

### Production Quality

- ✅ Comprehensive logging
- ✅ Error handling and recovery
- ✅ Input validation
- ✅ Output schemas
- ✅ Version tracking
- ✅ Health checks
- ✅ Monitoring hooks

---

## Contributing

To extend the pipeline:

1. **Add New Model**: Implement in `ai_ml/src/models/`
2. **Custom Features**: Add to `ai_ml/src/data/feature_engineering.py`
3. **New Dataset**: Create loader in `ai_ml/src/data/loaders.py`
4. **API Endpoint**: Add to `ai_ml/src/api/ml_service.py`
5. **Tests**: Add to `ai_ml/tests/`

---

## Support & References

**Datasets**:
- Elliptic: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
- BitcoinHeist: https://archive.ics.uci.edu/

**Models**:
- XGBoost: https://xgboost.readthedocs.io/
- PyTorch Geometric: https://pytorch-geometric.readthedocs.io/
- Scikit-Learn: https://scikit-learn.org/

**Explainability**:
- SHAP: https://shap.readthedocs.io/
- LIME: https://github.com/marcotcr/lime

---

**Last Updated**: September 3, 2024  
**Version**: 1.0.0  
**Maintainer**: CryptoTrace AI Engineering Team

