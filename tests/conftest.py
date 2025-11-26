"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test directories before running tests."""
    dirs = ["data", "memory", "models", "logs"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    yield
    # Cleanup can go here if needed


@pytest.fixture
def client():
    """Create FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
