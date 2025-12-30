"""
Pytest configuration and fixtures for app-text-gen tests.

Provides common fixtures and setup for unit and integration tests.
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Add src directory to path so tests can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def env_vars():
    """Provide access to environment variables."""
    return {
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'COSMOS_DB_ENDPOINT': os.getenv('COSMOS_DB_ENDPOINT'),
        'COSMOS_DB_KEY': os.getenv('COSMOS_DB_KEY'),
    }


@pytest.fixture(scope="session")
def cosmos_enabled(env_vars):
    """Check if Cosmos DB is configured."""
    return bool(env_vars['COSMOS_DB_ENDPOINT'] and env_vars['COSMOS_DB_KEY'])


@pytest.fixture(scope="session")
def azure_openai_enabled(env_vars):
    """Check if Azure OpenAI is configured."""
    return bool(env_vars['AZURE_OPENAI_API_KEY'] and env_vars['AZURE_OPENAI_ENDPOINT'])


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


# Markers for test organization
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual features"
    )
    config.addinivalue_line(
        "markers", "integration: Integration and end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


# Skip tests based on configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers and configuration."""
    for item in items:
        # Add markers based on test location
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)

