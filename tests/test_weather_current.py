import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("app.get_weather")
def test_weather_current_ok(mock_get_weather, client):
    mock_get_weather.return_value = {
        "source": "api",
        "data": {
            "resolvedAddress": "Alexandria, VA, US",
            "currentConditions": {
                "temp": 22.5,
                "conditions": "Partially cloudy",
                "humidity": 55,
                "windspeed": 5.0,
            },
        },
    }

    resp = client.get(
        "/weather/current?city=Alexandria&state=VA&country=US&unit=metric"
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["city"] == "Alexandria, VA, US"
    assert data["temperature"] == 22.5
    assert data["source"] == "api"
