.PHONY: help install generate prepare train evaluate predict dashboard test lint clean

help:
	@echo "CryptoTrace AI Development Commands:"
	@echo "  make install    - Install package and dependencies"
	@echo "  make generate   - Generate synthetic blockchain & network datasets"
	@echo "  make prepare    - Extract multi-modal features & build graph"
	@echo "  make train      - Fit XGBoost, Isolation Forest & GraphSAGE models"
	@echo "  make evaluate   - Run model evaluation on temporal test split"
	@echo "  make predict    - Run end-to-end inference and alert scoring"
	@echo "  make dashboard  - Launch Streamlit analytics dashboard"
	@echo "  make test       - Run pytest test suite"
	@echo "  make lint       - Run code formatting and lint checks"

install:
	pip install -e .[dev]

generate:
	python scripts/generate_synthetic_data.py --transactions 12000

prepare:
	python scripts/prepare_data.py --input data/synthetic/transactions.csv

train:
	python scripts/train.py

evaluate:
	python scripts/evaluate.py

predict:
	python scripts/predict.py --input data/synthetic/transactions.csv

dashboard:
	streamlit run dashboard/app.py

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	black --check src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
