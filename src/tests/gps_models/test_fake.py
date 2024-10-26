from unittest.mock import MagicMock, patch

import pytest

from geolocator.gps_modules.fake import FakeGPSModule
from geolocator.models.city import City


@patch("geolocator.gps_modules.fake.FakeGPSModule.retreive_fake_gps_data")
@patch("geolocator.gps_modules.fake.FakeGPSModule.get_current_city")
def test_read(mock_get_current_city: MagicMock, mock_retreive_fake_gps_data: MagicMock):
    fake_gps_module = FakeGPSModule()

    mock_retrieved_data = {
        "latitude": 33.7490,
        "longitude": -84.3880,
        "gps_time": 1640995200,
        "altitude": 100,
        "altitude_units": "m",
    }
    mock_city = City(
        name="Atlanta",
        state_id="GA",
        timezone="America/New_York",
    )

    mock_retreive_fake_gps_data.return_value = mock_retrieved_data
    mock_get_current_city.return_value = mock_city

    # Test read
    result = fake_gps_module.read()

    mock_retreive_fake_gps_data.assert_called_once()

    assert result.latitude == mock_retrieved_data["latitude"]
    assert result.longitude == mock_retrieved_data["longitude"]
    assert result.timestamp == 1640995200
    assert result.altitude == mock_retrieved_data["altitude"]
    assert result.altitude_units == mock_retrieved_data["altitude_units"]
    assert result.closest_city_name == "Atlanta, GA"
    assert result.closest_city_timezone == "America/New_York"
    assert result.local_time == "2021-12-31 19:00:00"


@patch("geolocator.gps_modules.fake.requests.get")
def test_retreive_fake_gps_data(mock_requests_get: MagicMock):
    fake_gps_module = FakeGPSModule()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "latitude": 33.7490,
        "longitude": -84.3880,
        "gps_time": 1640995200,
        "altitude": 100,
        "altitude_units": "m",
        "timestamp": 1640995200,
    }

    mock_requests_get.return_value = mock_response

    # Test retreive_fake_gps_data
    result = fake_gps_module.retreive_fake_gps_data()

    mock_requests_get.assert_called_once()

    assert result["latitude"] == 33.7490
    assert result["longitude"] == -84.3880
    assert result["gps_time"] == 1640995200
    assert result["altitude"] == 100
    assert result["altitude_units"] == "m"

    mock_response.json.assert_called_once()
