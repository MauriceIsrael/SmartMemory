# Contributing to SmartMemory

We welcome contributions to SmartMemory!

## Development Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd SmartMemory
    ```

2.  **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -e .[dev]
    ```

## Running Tests

We use `pytest` for testing.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/semantic_memory
```

## Code Style

We use `black` for formatting and `ruff` for linting.

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

## Type Checking

We use `mypy` for static type checking.

```bash
mypy src/
```

## Pull Request Process

1.  Fork the repository and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  Ensure the test suite passes.
4.  Make sure your code lints.
5.  Issue that pull request!
