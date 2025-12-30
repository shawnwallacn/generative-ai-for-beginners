# Tests Directory

Organized test suite for app-text-gen using pytest.

## Structure

```
tests/
├── unit/              # Unit and regression tests
│   ├── test_*.py      # Individual feature tests
│   └── test_*_fix.py  # Regression tests for bug fixes
│
├── integration/       # Integration and end-to-end tests
│   ├── test_*_complete.py    # Full system tests
│   ├── test_*_integration.py # Feature integration tests
│   └── test_*_feature.py     # Feature tests
│
├── conftest.py        # Pytest configuration and fixtures
└── __init__.py        # Package marker
```

## Running Tests

### All tests
```bash
pytest
```

### Unit tests only
```bash
pytest tests/unit/
```

### Integration tests only
```bash
pytest tests/integration/
```

### Specific test
```bash
pytest tests/unit/test_security.py
```

### With verbose output
```bash
pytest -v
```

### By marker
```bash
pytest -m unit        # Run unit tests
pytest -m integration # Run integration tests
pytest -m rag         # Run RAG-related tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Individual feature tests
- Regression tests for fixed bugs
- Security tests
- Audit logging tests
- Feature-specific tests (chunking, PDF parsing, etc.)

### Integration Tests (`tests/integration/`)
- Full end-to-end RAG system tests
- Multi-component integration tests
- Cosmos DB integration tests
- Search feature tests

## Configuration

Test configuration is in:
- `pytest.ini` - Pytest settings and markers
- `conftest.py` - Fixtures and test setup

## Fixtures Available

From `conftest.py`:
- `env_vars` - Environment variables
- `cosmos_enabled` - Check if Cosmos DB is configured
- `azure_openai_enabled` - Check if Azure OpenAI is configured
- `temp_dir` - Temporary directory for test files

## Adding New Tests

1. Create test file in appropriate directory:
   - `tests/unit/test_feature_name.py`
   - `tests/integration/test_integration_name.py`

2. Use pytest conventions:
   ```python
   def test_something():
       """Test description."""
       assert result == expected
   ```

3. Add appropriate markers:
   ```python
   @pytest.mark.unit
   @pytest.mark.security
   def test_security_feature():
       pass
   ```

## Test Results

Tests should output:
- ✓ for passed tests
- ✗ for failed tests
- Details of failures with error messages

Exit code:
- 0 = All tests passed
- 1 = Some tests failed

