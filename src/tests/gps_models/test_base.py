from unittest.mock import patch, MagicMock

import pytest

from geolocator.gps_modules.base import GPSModule


def test_read():
    gps_module = GPSModule()

    # Assert read raises NotImplementedError
    with pytest.raises(NotImplementedError):
        gps_module.read()


def test_get_altitude_data():
    gps_module = GPSModule()

    # Assert get_altitude_data raises NotImplementedError
    with pytest.raises(NotImplementedError):
        gps_module.get_altitude_data()


mock_session_instance = MagicMock()


class MockSession:
    def __init__(self, engine):
        self.instance = mock_session_instance
        self.engine = engine

    def __enter__(self):
        return self.instance

    def __exit__(self, exc_type, exc_value, traceback):
        pass


@patch("geolocator.gps_modules.base.get_sql_engine")
@patch("geolocator.gps_modules.base.get_closest_city")
@patch("geolocator.gps_modules.base.Session", MockSession)
def test_get_current_city(
    mock_get_closest_city: MagicMock,
    mock_get_sql_engine: MagicMock,
):
    gps_module = GPSModule()
    mock_city = MagicMock()
    mock_lat = 33.7490
    mock_lng = -84.3880

    mock_get_closest_city.return_value = mock_city

    # Test get_current_city
    gps_module.get_current_city(mock_lat, mock_lng)

    mock_get_sql_engine.assert_called_once()
    mock_get_closest_city.assert_called_once_with(
        mock_session_instance, mock_lat, mock_lng
    )
