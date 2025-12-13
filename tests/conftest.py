import pytest
import requests_mock as rm
from app.app import app


@pytest.fixture
def client():
    """Test client fixture with testing mode enabled"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_api():
    """Mock external API calls for testing"""
    with rm.Mocker() as mock:
        yield mock
