"""
Flask Routes Tests
Tests critical endpoints for weather and places functionality
"""

import pytest


# -------------------------
# Phase 1: Weather Route Tests
# -------------------------


def test_get_weather_endpoint(client, mock_api):
    """ROUTE-01: /weather/current?lat=X&lng=Y returns JSON"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={
            "temperature": {"degrees": 20, "unit": "CELSIUS"},
            "relativeHumidity": 65,
        },
        status_code=200,
    )

    response = client.get("/weather/current?lat=51.5074&lng=-0.1278")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "temperature" in data


def test_daily_weather_endpoint(client, mock_api):
    """Test daily forecast endpoint"""
    mock_api.get(
        "https://weather.googleapis.com/v1/forecast/days:lookup",
        json={
            "forecastDays": [
                {
                    "maxTemperature": {"degrees": 25, "unit": "CELSIUS"},
                    "minTemperature": {"degrees": 15, "unit": "CELSIUS"},
                    "daytimeForecast": {"weatherCondition": {"type": "SUNNY"}},
                }
            ]
        },
        status_code=200,
    )

    response = client.get("/weather/daily?lat=40.7128&lng=-74.0060")

    assert response.status_code == 200
    data = response.get_json()
    assert "forecastDays" in data


def test_hourly_weather_endpoint(client, mock_api):
    """Test hourly forecast endpoint"""
    mock_api.get(
        "https://weather.googleapis.com/v1/forecast/hours:lookup",
        json={"forecastHours": [{"temperature": {"degrees": 22, "unit": "CELSIUS"}}]},
        status_code=200,
    )

    response = client.get("/weather/hourly?lat=48.8566&lng=2.3522")

    assert response.status_code == 200
    data = response.get_json()
    assert "forecastHours" in data


def test_missing_coordinates(client):
    """Test weather endpoint with missing coordinates"""
    response = client.get("/weather/current?lat=51.5074")  # Missing lng

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "lng" in data["error"]


# -------------------------
# Phase 1: Places/Autocomplete Tests
# -------------------------


def test_autocomplete_endpoint(client, mock_api):
    """Test place autocomplete search"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={
            "predictions": [
                {
                    "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
                    "description": "London, UK",
                    "matched_substrings": [{"length": 6, "offset": 0}],
                    "structured_formatting": {
                        "main_text": "London",
                        "main_text_matched_substrings": [{"length": 6, "offset": 0}],
                        "secondary_text": "UK",
                    },
                    "terms": [
                        {"offset": 0, "value": "London"},
                        {"offset": 8, "value": "UK"},
                    ],
                    "types": ["locality", "political", "geocode"],
                }
            ],
            "status": "OK",
        },
        status_code=200,
    )

    response = client.get("/autocomplete?query=London")

    assert response.status_code == 200
    data = response.get_json()
    assert "predictions" in data


def test_place_details_endpoint(client, mock_api):
    """Test getting place details by place_id"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        json={
            "status": "OK",
            "html_attributions": [],
            "result": {
                "name": "London",
                "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
                "formatted_address": "London, UK",
                "geometry": {
                    "location": {"lat": 51.5074, "lng": -0.1278},
                    "viewport": {
                        "northeast": {"lat": 51.6457, "lng": -0.0062},
                        "southwest": {"lat": 51.3827, "lng": -0.2808},
                    },
                },
                "types": ["locality", "political", "geocode"],
                "url": "https://maps.google.com/?cid=12345",
            },
        },
        status_code=200,
    )

    response = client.get("/place_details?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "London"
    assert "geometry" in data


def test_place_details_invalid_place_id(client, mock_api):
    """Test place details with invalid place_id"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        json={"status": "INVALID_REQUEST"},
        status_code=200,
    )

    response = client.get("/place_details?place_id=invalid")

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


# -------------------------
# Phase 1: Icon Route Tests
# -------------------------


def test_icon_endpoint(client, mock_api):
    """Test weather icon proxy endpoint"""
    mock_svg = b"<svg>test icon</svg>"

    mock_api.get(
        "https://maps.gstatic.com/weather/v1/sunny.svg",
        content=mock_svg,
        status_code=200,
    )

    response = client.get("/icon?icon=sunny")

    assert response.status_code == 200
    assert response.content_type == "image/svg+xml"
    assert response.data == mock_svg


def test_icon_dark_mode(client, mock_api):
    """Test weather icon with dark mode"""
    mock_svg = b"<svg>dark icon</svg>"

    mock_api.get(
        "https://maps.gstatic.com/weather/v1/cloudy_dark.svg",
        content=mock_svg,
        status_code=200,
    )

    response = client.get("/icon?icon=cloudy&dark=true")

    assert response.status_code == 200
    assert response.data == mock_svg


def test_icon_invalid_name(client):
    """Test icon endpoint with invalid icon name"""
    response = client.get("/icon?icon=malicious_script")

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid icon"


# -------------------------
# Route Error Handling
# -------------------------


def test_missing_query_params(client):
    """Test endpoints with missing required parameters"""
    endpoints = [
        "/weather/current",  # Missing lat/lng
        "/autocomplete",  # Missing query
        "/place_details",  # Missing place_id
        "/icon",  # Missing icon
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
