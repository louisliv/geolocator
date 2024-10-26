from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from geolocator import client


@pytest.mark.parametrize(
    "lat1, lng1, lat2, lng2, expected",
    [
        (33.7490, -84.3880, 33.7490, -84.3880, 0.0),
        (33.7490, -84.3880, 33.7480, -84.3880, 0.11119492664508969),
        (33.7490, -84.3880, 33.7490, -84.3870, 0.09245628073807766),
        (33.7490, -84.3880, 33.7480, -84.3870, 0.14461180879468286),
    ],
)
def test_haversine(lat1, lng1, lat2, lng2, expected):
    result = client.haversine(lat1, lng1, lat2, lng2)

    assert result == expected


@pytest.mark.parametrize(
    "lat, lng, expected_city_name, expected_state_id",
    [
        (33.7490, -84.3880, "Atlanta", "GA"),
        (34.0522, -118.2437, "Vernon", "CA"),
        (40.7128, -74.0060, "Hoboken", "NJ"),
        (41.8781, -87.6298, "Chicago", "IL"),
        (29.7604, -95.3698, "Houston", "TX")
    ],
)
def test_get_closest_city(lat, lng, expected_city_name, expected_state_id):
    sql_engine = client.get_sql_engine()

    with Session(sql_engine) as session:
        result = client.get_closest_city(session, lat, lng)

        assert result.name == expected_city_name
        assert result.state_id == expected_state_id
