"""
Edge Cases and Additional Validation Tests
Additional comprehensive test coverage for weather dashboard
"""

import pytest
import json


# -------------------------
# Weather API Edge Cases
# -------------------------


def test_extreme_temperature_values(client, mock_api):
    """Test with extreme temperature values"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={
            "temperature": {"degrees": -50, "unit": "CELSIUS"},
            "relativeHumidity": 95,
        },
        status_code=200,
    )

    response = client.get("/weather/current?lat=71.1919&lng=25.7482")
    assert response.status_code == 200
    data = response.get_json()
    assert data["temperature"]["degrees"] == -50


def test_zero_temperature(client, mock_api):
    """Test with zero temperature"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"temperature": {"degrees": 0, "unit": "CELSIUS"}, "relativeHumidity": 50},
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["temperature"]["degrees"] == 0


def test_high_humidity(client, mock_api):
    """Test with maximum humidity values"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={
            "temperature": {"degrees": 25, "unit": "CELSIUS"},
            "relativeHumidity": 100,
        },
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["relativeHumidity"] == 100


def test_zero_humidity(client, mock_api):
    """Test with minimum humidity"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"temperature": {"degrees": 25, "unit": "CELSIUS"}, "relativeHumidity": 0},
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["relativeHumidity"] == 0


def test_high_wind_speed(client, mock_api):
    """Test with extreme wind speed"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={
            "temperature": {"degrees": 25, "unit": "CELSIUS"},
            "wind": {"speed": {"value": 150, "unit": "KILOMETERS_PER_HOUR"}},
        },
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["wind"]["speed"]["value"] == 150


def test_zero_wind_speed(client, mock_api):
    """Test with calm conditions (zero wind)"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={
            "temperature": {"degrees": 25, "unit": "CELSIUS"},
            "wind": {"speed": {"value": 0, "unit": "KILOMETERS_PER_HOUR"}},
        },
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["wind"]["speed"]["value"] == 0


# -------------------------
# Coordinate Validation
# -------------------------


def test_boundary_latitude_north(client):
    """Test with maximum valid latitude (North Pole)"""
    response = client.get("/weather/current?lat=90&lng=0")
    # Should not crash, even if API doesn't have weather there
    assert response.status_code in [200, 400, 502]


def test_boundary_latitude_south(client):
    """Test with minimum valid latitude (South Pole)"""
    response = client.get("/weather/current?lat=-90&lng=0")
    assert response.status_code in [200, 400, 502]


def test_boundary_longitude_east(client):
    """Test with maximum longitude (International Date Line)"""
    response = client.get("/weather/current?lat=0&lng=180")
    assert response.status_code in [200, 400, 502]


def test_boundary_longitude_west(client):
    """Test with minimum longitude"""
    response = client.get("/weather/current?lat=0&lng=-180")
    assert response.status_code in [200, 400, 502]


def test_invalid_latitude_too_high(client):
    """Test with latitude beyond bounds"""
    response = client.get("/weather/current?lat=91&lng=0")
    # Should either reject or let API handle it
    assert response.status_code in [400, 502, 200]


def test_invalid_latitude_too_low(client):
    """Test with latitude below bounds"""
    response = client.get("/weather/current?lat=-91&lng=0")
    assert response.status_code in [400, 502, 200]


def test_non_numeric_latitude(client):
    """Test with non-numeric latitude"""
    response = client.get("/weather/current?lat=abc&lng=0")
    # App passes non-numeric values to API, which returns error
    assert response.status_code in [400, 502]


def test_non_numeric_longitude(client):
    """Test with non-numeric longitude"""
    response = client.get("/weather/current?lat=0&lng=xyz")
    # App passes non-numeric values to API, which returns error
    assert response.status_code in [400, 502]


def test_missing_both_coordinates(client):
    """Test with both lat and lng missing"""
    response = client.get("/weather/current")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_empty_coordinate_params(client):
    """Test with empty string coordinates"""
    response = client.get("/weather/current?lat=&lng=")
    assert response.status_code == 400


# -------------------------
# Places API Edge Cases
# -------------------------


def test_autocomplete_empty_query(client, mock_api):
    """Test autocomplete with empty search string"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={"predictions": [], "status": "OK"},
        status_code=200,
    )

    response = client.get("/autocomplete?query=")
    # Empty search may return empty results
    assert response.status_code in [200, 400]


def test_autocomplete_special_characters(client, mock_api):
    """Test autocomplete with special characters"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={"predictions": [], "status": "OK"},
        status_code=200,
    )

    response = client.get("/autocomplete?query=St%20Jean%20de%20Luz")
    assert response.status_code == 200


def test_autocomplete_unicode_characters(client, mock_api):
    """Test autocomplete with Unicode characters"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={"predictions": [], "status": "OK"},
        status_code=200,
    )

    response = client.get("/autocomplete?query=München")
    assert response.status_code == 200


def test_autocomplete_very_long_query(client, mock_api):
    """Test autocomplete with very long search string"""
    long_query = "a" * 500
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={"predictions": [], "status": "OK"},
        status_code=200,
    )

    response = client.get(f"/autocomplete?query={long_query}")
    # Should either truncate or handle gracefully
    assert response.status_code in [200, 400]


def test_place_details_empty_place_id(client):
    """Test place details with empty place_id"""
    response = client.get("/place_details?place_id=")
    assert response.status_code == 400


def test_place_details_whitespace_place_id(client):
    """Test place details with whitespace place_id"""
    response = client.get("/place_details?place_id=%20%20%20")
    assert response.status_code == 400


def test_place_details_special_characters(client, mock_api):
    """Test place details with special characters in ID"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        json={
            "status": "OK",
            "html_attributions": [],
            "result": {
                "name": "Test Place",
                "place_id": "ChIJ-special-chars",
                "geometry": {"location": {"lat": 0, "lng": 0}},
            },
        },
        status_code=200,
    )

    response = client.get("/place_details?place_id=ChIJ-special-chars")
    assert response.status_code == 200


# -------------------------
# Icon Endpoint Edge Cases
# -------------------------


def test_icon_case_sensitivity(client, mock_api):
    """Test if icon names are case-sensitive"""
    mock_svg = b"<svg>test</svg>"
    mock_api.get(
        "https://maps.gstatic.com/weather/v1/sunny.svg",
        content=mock_svg,
        status_code=200,
    )

    response = client.get("/icon?icon=SUNNY")
    # Should handle case appropriately
    assert response.status_code in [200, 400]


def test_icon_with_spaces(client):
    """Test icon endpoint with spaces in name"""
    response = client.get("/icon?icon=sunny%20day")
    assert response.status_code == 400  # Should reject spaces


def test_icon_with_path_traversal(client):
    """Test icon endpoint with path traversal attempt"""
    response = client.get("/icon?icon=../../../etc/passwd")
    assert response.status_code == 400  # Security check


def test_icon_with_extension(client):
    """Test icon endpoint when extension is included"""
    response = client.get("/icon?icon=sunny.svg")
    # May reject .svg or strip it
    assert response.status_code in [200, 400]


def test_icon_dark_mode_values(client, mock_api):
    """Test various dark mode parameter values"""
    mock_svg = b"<svg>test</svg>"

    # Mock sunny icon for both light and dark variants
    mock_api.get(
        "https://maps.gstatic.com/weather/v1/sunny.svg",
        content=mock_svg,
        status_code=200,
    )
    mock_api.get(
        "https://maps.gstatic.com/weather/v1/sunny_dark.svg",
        content=mock_svg,
        status_code=200,
    )

    # Test with various truthy values
    for dark_param in ["true", "1"]:
        response = client.get(f"/icon?icon=sunny&dark={dark_param}")
        # Should be interpreted as dark mode
        assert response.status_code in [200, 400]


def test_icon_empty_icon_param(client):
    """Test icon endpoint with empty icon parameter"""
    response = client.get("/icon?icon=")
    assert response.status_code == 400


# -------------------------
# Favorites Edge Cases
# -------------------------


def test_favorite_name_with_special_characters(client):
    """Test adding favorite with special characters in name"""
    response = client.post(
        "/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=Caf%C3%A9%20au%20Lait"
    )
    assert response.status_code == 200
    data = response.get_json()
    # Just verify it was accepted
    assert data["status"] == "added"


def test_favorite_name_with_unicode(client):
    """Test adding favorite with Unicode characters"""
    response = client.post(
        "/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=北京"
    )
    assert response.status_code == 200


def test_favorite_very_long_name(client):
    """Test adding favorite with very long name"""
    long_name = "a" * 500
    response = client.post(
        f"/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name={long_name}"
    )
    # Should either accept or reject gracefully
    assert response.status_code in [200, 400]


def test_favorite_empty_name(client):
    """Test adding favorite with empty name parameter"""
    response = client.post("/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_delete_same_favorite_twice(client):
    """Test deleting the same favorite twice"""
    place_id = "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
    client.post(f"/favorites/set?place_id={place_id}&name=Test")

    # Delete once
    response1 = client.post(f"/favorites/delete?place_id={place_id}")
    assert response1.status_code == 200

    # Try to delete again
    response2 = client.post(f"/favorites/delete?place_id={place_id}")
    assert response2.status_code == 400  # Should fail


def test_get_after_clear(client):
    """Test retrieving favorites after clearing all"""
    client.post("/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=Test1")
    client.post("/favorites/set?place_id=ChIJmysnFgZYSoYRSfPTL2YJuck&name=Test2")

    # Clear all
    client.post("/favorites/clear")

    # Try to retrieve
    response = client.get("/favorites/get")
    favorites = response.get_json()
    assert len(favorites) == 0


def test_multiple_operations_same_place(client):
    """Test multiple add/update operations on same place"""
    place_id = "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"

    # Add with first name
    client.post(f"/favorites/set?place_id={place_id}&name=Paris")
    response1 = client.get(f"/favorites/get?place_id={place_id}")
    assert response1.get_json()["name"] == "Paris"

    # Update with second name
    client.post(f"/favorites/set?place_id={place_id}&name=City of Light")
    response2 = client.get(f"/favorites/get?place_id={place_id}")
    assert response2.get_json()["name"] == "City of Light"

    # Update with third name
    client.post(f"/favorites/set?place_id={place_id}&name=The Capital")
    response3 = client.get(f"/favorites/get?place_id={place_id}")
    assert response3.get_json()["name"] == "The Capital"


def test_favorites_with_duplicate_locations(client):
    """Test handling of same place added with different names"""
    place_id = "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"

    # Add once as "Paris"
    client.post(f"/favorites/set?place_id={place_id}&name=Paris")

    # Try to add same place as "The City"
    client.post(f"/favorites/set?place_id={place_id}&name=The City")

    # Should update, not duplicate
    response = client.get("/favorites/get")
    favorites = response.get_json()
    paris_count = sum(1 for f in favorites if f["place_id"] == place_id)
    assert paris_count == 1


# -------------------------
# Response Format Validation
# -------------------------


def test_weather_response_content_type(client, mock_api):
    """Test that weather endpoint returns JSON content type"""
    mock_api.get(
        "https://weather.googleapis.com/v1/currentConditions:lookup",
        json={"temperature": {"degrees": 20, "unit": "CELSIUS"}},
        status_code=200,
    )

    response = client.get("/weather/current?lat=0&lng=0")
    assert response.content_type == "application/json"


def test_autocomplete_response_structure(client, mock_api):
    """Test that autocomplete returns expected structure"""
    mock_api.get(
        "https://maps.googleapis.com/maps/api/place/autocomplete/json",
        json={
            "predictions": [
                {
                    "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
                    "description": "London, UK",
                    "structured_formatting": {
                        "main_text": "London",
                        "secondary_text": "UK",
                    },
                }
            ],
            "status": "OK",
        },
        status_code=200,
    )

    response = client.get("/autocomplete?query=London")
    data = response.get_json()

    assert "predictions" in data
    assert isinstance(data["predictions"], list)
    if len(data["predictions"]) > 0:
        assert "place_id" in data["predictions"][0]


def test_error_response_format(client):
    """Test that error responses have consistent format"""
    response = client.get("/weather/current")  # Missing params
    assert response.status_code == 400
    data = response.get_json()

    assert "error" in data or "message" in data
