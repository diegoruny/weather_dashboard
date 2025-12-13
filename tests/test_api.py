"""
API Connection and Data Parsing Tests
Tests critical path for Google Weather API integration
"""

import pytest
import requests


# -------------------------
# Smoke Test
# -------------------------


def test_app_loads(client):
    """Smoke test - systems working"""
    response = client.get("/")
    assert response.status_code == 200


# -------------------------
# Phase 1: API Connection Tests
# -------------------------


def test_api_connection_success(client, mock_api):
    """API-01: Can we reach Google Weather API?"""
    # Mock successful API response
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"temperature": {"degrees": 20, "unit": "CELSIUS"}},
        status_code=200,
    )

    response = client.get("/weather/current?lat=51.5074&lng=-0.1278")
    assert response.status_code == 200
    assert mock_api.called


def test_api_key_valid(client, mock_api):
    """API-02: Does our API key authenticate?"""
    # Mock API with authentication success
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"temperature": {"degrees": 20, "unit": "CELSIUS"}},
        status_code=200,
    )

    response = client.get("/weather/current?lat=51.5074&lng=-0.1278")
    assert response.status_code == 200

    # Verify API key was sent in request
    assert mock_api.last_request.qs.get("key") is not None


def test_api_response_format(client, mock_api):
    """API-03: Does API return expected JSON structure?"""
    expected_data = {
        "temperature": {"degrees": 20, "unit": "CELSIUS"},
        "relativeHumidity": 65,
        "weatherCondition": {"type": "CLEAR"},
    }

    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json=expected_data,
        status_code=200,
    )

    response = client.get("/weather/current?lat=51.5074&lng=-0.1278")
    data = response.get_json()

    assert response.status_code == 200
    assert "temperature" in data
    assert data["temperature"]["degrees"] == 20


# -------------------------
# Phase 1: Data Parsing Tests
# -------------------------


def test_parse_valid_weather_data(client, mock_api):
    """PARSE-01: Valid API response → correct Python dict"""
    valid_response = {
        "temperature": {"degrees": 22.5, "unit": "CELSIUS"},
        "relativeHumidity": 70,
        "wind": {"speed": {"value": 5.2, "unit": "KILOMETERS_PER_HOUR"}},
    }

    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json=valid_response,
        status_code=200,
    )

    response = client.get("/weather/current?lat=40.7128&lng=-74.0060")
    data = response.get_json()

    assert response.status_code == 200
    assert data["temperature"]["degrees"] == 22.5
    assert data["relativeHumidity"] == 70
    assert data["wind"]["speed"]["value"] == 5.2


def test_parse_missing_fields(client, mock_api):
    """PARSE-02: Missing temperature field → doesn't crash"""
    incomplete_response = {
        "relativeHumidity": 70
        # Missing temperature field
    }

    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json=incomplete_response,
        status_code=200,
    )

    response = client.get("/weather/current?lat=40.7128&lng=-74.0060")

    # Should not crash - returns data as-is
    assert response.status_code == 200
    data = response.get_json()
    assert "temperature" not in data
    assert "relativeHumidity" in data


def test_parse_malformed_response(client, mock_api):
    """PARSE-03: Garbage data → returns error message"""
    # Simulate API returning 500 error
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"error": "Internal server error"},
        status_code=500,
    )

    response = client.get("/weather/current?lat=40.7128&lng=-74.0060")

    assert response.status_code == 502  # Our app returns 502 for external errors
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "External service error"


# -------------------------
# Additional Edge Cases
# -------------------------


def test_api_timeout(client, mock_api):
    """Test API timeout handling"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        exc=requests.Timeout,
    )

    response = client.get("/weather/current?lat=40.7128&lng=-74.0060")

    assert response.status_code == 504
    data = response.get_json()
    assert data["error"] == "External service timed out"


def test_api_connection_error(client, mock_api):
    """Test network connection error handling"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        exc=requests.ConnectionError,
    )

    response = client.get("/weather/current?lat=40.7128&lng=-74.0060")

    assert response.status_code == 502
    data = response.get_json()
    assert data["error"] == "Service unavailable"
