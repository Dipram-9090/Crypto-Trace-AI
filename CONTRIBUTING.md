# Contributing to CryptoTrace AI

Thank you for your interest in contributing to CryptoTrace AI!

## Development Workflow

1. Fork and clone the repository.
2. Install dependencies in editable development mode:
   ```bash
   pip install -e .[dev]
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Run tests and linters before submitting a PR:
   ```bash
   pytest tests/
   black --check src/ tests/
   ruff check src/ tests/
   ```
5. Submit a pull request detailing your changes and verification steps.
