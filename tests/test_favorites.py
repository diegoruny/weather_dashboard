"""
Cookie/Favorites Tests
Tests favorites management and cookie persistence
"""

import pytest
import json


# -------------------------
# Phase 1: Cookie/Favorites Tests
# -------------------------


def test_add_favorite_to_cookies(client):
    """COOKIE-01: Can write favorite to browser cookie"""
    response = client.post(
        "/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=Paris"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "added"

    # Verify cookie was set in response
    assert "favorites" in response.headers.get("Set-Cookie", "")


def test_read_favorites_from_cookies(client):
    """COOKIE-02: Can retrieve saved favorites list"""
    # First, add a favorite
    client.post("/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=London")
    client.post("/favorites/set?place_id=ChIJmysnFgZYSoYRSfPTL2YJuck&name=Paris")

    # Now retrieve favorites
    response = client.get("/favorites/get")

    assert response.status_code == 200
    favorites = response.get_json()
    assert len(favorites) == 2
    assert favorites[0]["name"] == "London"
    assert favorites[0]["place_id"] == "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
    assert favorites[1]["name"] == "Paris"


def test_get_single_favorite(client):
    """Test retrieving a single favorite by place_id"""
    # Add favorite
    client.post("/favorites/set?place_id=ChIJ4zHP-Sije4gRBDEsVxunOWg&name=Tokyo")

    # Get specific favorite
    response = client.get("/favorites/get?place_id=ChIJ4zHP-Sije4gRBDEsVxunOWg")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Tokyo"
    assert data["place_id"] == "ChIJ4zHP-Sije4gRBDEsVxunOWg"


def test_get_nonexistent_favorite(client):
    """Test retrieving a favorite that doesn't exist"""
    response = client.get("/favorites/get?place_id=nonexistent")

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_existing_favorite(client):
    """Test updating an existing favorite's name"""
    # Add favorite
    client.post("/favorites/set?place_id=ChIJsamfQbVtLIgR-X18G75Hyi0&name=New York")

    # Update it
    response = client.post(
        "/favorites/set?place_id=ChIJsamfQbVtLIgR-X18G75Hyi0&name=NYC"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "updated"

    # Verify update
    response = client.get("/favorites/get?place_id=ChIJsamfQbVtLIgR-X18G75Hyi0")
    data = response.get_json()
    assert data["name"] == "NYC"


def test_remove_favorite_endpoint(client):
    """ROUTE-03: /favorites/delete removes from cookies"""
    # Add favorite
    client.post("/favorites/set?place_id=ChIJsU7_xMfKQ4gReI89RJn0-RQ&name=Berlin")

    # Verify it exists
    response = client.get("/favorites/get?place_id=ChIJsU7_xMfKQ4gReI89RJn0-RQ")
    assert response.status_code == 200

    # Remove it
    response = client.post("/favorites/delete?place_id=ChIJsU7_xMfKQ4gReI89RJn0-RQ")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "deleted"

    # Verify it's gone
    response = client.get("/favorites/get?place_id=ChIJsU7_xMfKQ4gReI89RJn0-RQ")
    assert response.status_code == 400


def test_remove_nonexistent_favorite(client):
    """Test deleting a favorite that doesn't exist"""
    response = client.post("/favorites/delete?place_id=nonexistent")

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Not found"


def test_clear_all_favorites(client):
    """Test clearing all favorites at once"""
    # Add multiple favorites
    client.post("/favorites/set?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&name=Rome")
    client.post("/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&name=Madrid")
    client.post("/favorites/set?place_id=ChIJmysnFgZYSoYRSfPTL2YJuck&name=Vienna")

    # Clear all
    response = client.post("/favorites/clear")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "cleared"

    # Verify all are gone
    response = client.get("/favorites/get")
    favorites = response.get_json()
    assert len(favorites) == 0


def test_favorites_limit(client):
    """Test that favorites respect the maximum limit"""
    from app.config import DebugConfig

    max_favorites = DebugConfig.MAX_FAVORITES

    # Realistic place IDs from Google API
    real_place_ids = [
        "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
        "ChIJmysnFgZYSoYRSfPTL2YJuck",
        "ChIJ4zHP-Sije4gRBDEsVxunOWg",
        "ChIJsamfQbVtLIgR-X18G75Hyi0",
        "ChIJsU7_xMfKQ4gReI89RJn0-RQ",
        "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "ChIJmysnFgZYSoYRSfPTL2YJuckExtra1",
        "ChIJ4zHP-Sije4gRBDEsVxunOWgExtra2",
        "ChIJsamfQbVtLIgR-X18G75HyiExtra3",
        "ChIJsU7_xMfKQ4gReI89RJn0-RQExtra4",
    ]

    # Add favorites up to the limit
    for i in range(max_favorites):
        response = client.post(
            f"/favorites/set?place_id={real_place_ids[i]}&name=City_{i}"
        )
        assert response.status_code == 200

    # Try to add one more - should fail
    response = client.post(
        f"/favorites/set?place_id=ChIJExtraPlaceIdNotReal&name=Extra"
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Limit reached"


def test_missing_parameters_in_favorites(client):
    """Test favorites endpoints with missing parameters"""
    # Missing both parameters
    response = client.post("/favorites/set")
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing" in data["error"]

    # Missing name
    response = client.post("/favorites/set?place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ")
    assert response.status_code == 400

    # Missing place_id
    response = client.post("/favorites/set?name=London")
    assert response.status_code == 400

    # Missing place_id in delete
    response = client.post("/favorites/delete")
    assert response.status_code == 400


def test_favorites_cookie_persistence(client):
    """Test that favorites persist across multiple requests"""
    # Add favorites in multiple requests
    client.post("/favorites/set?place_id=ChIJ4zHP-Sije4gRBDEsVxunOWg&name=City_A")
    client.post("/favorites/set?place_id=ChIJsamfQbVtLIgR-X18G75Hyi0&name=City_B")

    # Retrieve in a separate request
    response = client.get("/favorites/get")
    favorites = response.get_json()

    assert len(favorites) == 2
    place_ids = [fav["place_id"] for fav in favorites]
    assert "ChIJ4zHP-Sije4gRBDEsVxunOWg" in place_ids
    assert "ChIJsamfQbVtLIgR-X18G75Hyi0" in place_ids


def test_favorites_sanitization(client):
    """Test that invalid favorite data is filtered out"""
    # Manually create corrupted cookie data
    client.set_cookie(
        "favorites",
        json.dumps(
            [
                {"place_id": "valid1", "name": "Valid City"},
                {"place_id": "valid2"},  # Missing name - invalid
                {"name": "No ID"},  # Missing place_id - invalid
                "invalid_string",  # Not a dict - invalid
                {
                    "place_id": 123,
                    "name": "Wrong Type",
                },  # place_id not string - invalid
            ]
        ),
    )

    # Should only return the valid favorite
    response = client.get("/favorites/get")
    favorites = response.get_json()

    assert len(favorites) == 1
    assert favorites[0]["place_id"] == "valid1"
