# 🛠️ Development & Operational Guide

Guidelines for setting up, building, testing, and deploying CryptoTrace AI.

---

## 1. Local Environment Setup

```bash
# Clone the repository
git clone https://github.com/rajdeepcodeshere247/Crypto-Trace-AI.git
cd Crypto-Trace-AI

# Install in editable mode with development dependencies
pip install -e .[dev]
```

---

## 2. Running Automated Tests & Linters

```bash
# Run the test suite
pytest tests/ -v

# Run code style and format checks
ruff check src/ tests/
black --check src/ tests/
```

---

## 3. End-to-End Pipeline Execution

```bash
# 1. Generate synthetic network & blockchain data
make generate

# 2. Extract features and build graph
make prepare

# 3. Fit all supervised, unsupervised, and GNN models
make train

# 4. Evaluate models on held-out temporal splits
make evaluate

# 5. Execute inference and generate alerts
make predict

# 6. Launch forensic analytics dashboard
make dashboard
```

---

## 4. Docker Deployment

```bash
docker-compose up --build
```
Navigate to `http://localhost:8501` to view the Streamlit interface.
