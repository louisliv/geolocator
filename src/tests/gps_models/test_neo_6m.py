from unittest.mock import MagicMock, patch

import pytest
import pynmea2

from geolocator.gps_modules.neo_6m import Neo6MGPSModule, GPSData

GGA_MESSAGE = (
    "$GPGGA,184353.07,1929.045,S,02410.506,E,0,0,,0.0,M,0.0,M,,0000*57".encode()
)

RMC_MESSAGE = (
    "$GPRMC,184353.07,A,1929.045,S,02410.506,E,0.0,0.0,010170,0.0,E*4B".encode()
)


@patch("geolocator.gps_modules.neo_6m.serial.Serial")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._handle_rmc_data")
def test_read(
    mock_handle_rmc_data: MagicMock,
    mock_serial: MagicMock,
):
    mock_serial.return_value.readline.return_value = RMC_MESSAGE

    mock_rmc_data = MagicMock()

    mock_handle_rmc_data.return_value = mock_rmc_data

    neo_6m_gps_module = Neo6MGPSModule()

    # Test read
    result = neo_6m_gps_module.read()

    assert result == mock_rmc_data


@patch("geolocator.gps_modules.neo_6m.serial.Serial")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._handle_gga_data")
def test_get_altitude_data(
    mock_handle_gga_data: MagicMock,
    mock_serial: MagicMock,
):
    mock_serial.return_value.readline.return_value = GGA_MESSAGE

    mock_gga_data = MagicMock()

    mock_handle_gga_data.return_value = mock_gga_data

    neo_6m_gps_module = Neo6MGPSModule()

    # Test get_altitude_data
    result = neo_6m_gps_module.get_altitude_data()

    assert result == mock_gga_data


@patch("geolocator.gps_modules.neo_6m.serial.Serial")
def test_parse_gps_data(
    mock_serial: MagicMock,
):
    neo_6m_gps_module = Neo6MGPSModule()

    rmc_data = pynmea2.parse(RMC_MESSAGE.decode())
    gga_data = pynmea2.parse(GGA_MESSAGE.decode())

    # Test _parse_gps_data
    result = neo_6m_gps_module._parse_gps_data(rmc_data)

    assert result.latitude == rmc_data.latitude
    assert result.longitude == rmc_data.longitude
    assert result.timestamp == rmc_data.timestamp
    assert result.closest_city_name == "Candelero Abajo, PR"
    assert result.closest_city_timezone == "America/Puerto_Rico"

    result = neo_6m_gps_module._parse_gps_data(gga_data)

    assert result.latitude == gga_data.latitude
    assert result.longitude == gga_data.longitude
    assert result.timestamp == gga_data.timestamp
    assert result.closest_city_name == "Candelero Abajo, PR"
    assert result.closest_city_timezone == "America/Puerto_Rico"


@patch("geolocator.gps_modules.neo_6m.serial.Serial")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._parse_gps_data")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._check_land_speed")
@pytest.mark.parametrize(
    "check_land_speed_result",
    [
        True,
        False,
    ],
)
def test_handle_rmc_data(
    mock_check_land_speed: MagicMock,
    mock_parse_gps_data: MagicMock,
    mock_serial: MagicMock,
    check_land_speed_result: bool,
):
    mock_rmc_data = MagicMock()
    mock_parse_gps_data.return_value = mock_rmc_data

    neo_6m_gps_module = Neo6MGPSModule()

    mock_check_land_speed.return_value = check_land_speed_result

    # Test _handle_rmc_data
    if check_land_speed_result:
        result = neo_6m_gps_module._handle_rmc_data(RMC_MESSAGE.decode())

        assert result == mock_rmc_data
    else:
        result = neo_6m_gps_module._handle_rmc_data(RMC_MESSAGE.decode())

        assert result is None


@patch("geolocator.gps_modules.neo_6m.serial.Serial")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._parse_gps_data")
@patch("geolocator.gps_modules.neo_6m.Neo6MGPSModule._check_hdop_data")
@pytest.mark.parametrize(
    "check_hdop_data_result",
    [
        True,
        False,
    ],
)
def test_handle_gga_data(
    mock_check_hdop_data: MagicMock,
    mock_parse_gps_data: MagicMock,
    mock_serial: MagicMock,
    check_hdop_data_result: bool,
):
    mock_gga_data = GPSData(
        latitude=33.7490,
        longitude=-84.3880,
        gps_time=1640995200,
        closest_city_name="Atlanta, GA",
        timestamp=1640995200,
        closest_city_timezone="America/New_York",
        local_time="2021-12-31 19:00:00",
    )
    mock_parse_gps_data.return_value = mock_gga_data

    neo_6m_gps_module = Neo6MGPSModule()

    mock_check_hdop_data.return_value = check_hdop_data_result

    # Test _handle_gga_data
    if check_hdop_data_result:
        result = neo_6m_gps_module._handle_gga_data(GGA_MESSAGE.decode())

        assert result.latitude == mock_gga_data.latitude
        assert result.longitude == mock_gga_data.longitude
        assert result.timestamp == mock_gga_data.timestamp
        assert result.closest_city_name == mock_gga_data.closest_city_name
        assert result.closest_city_timezone == mock_gga_data.closest_city_timezone
        assert result.local_time == mock_gga_data.local_time
        assert result.altitude == 0.0
        assert result.altitude_units == "M"
    else:
        result = neo_6m_gps_module._handle_gga_data(GGA_MESSAGE.decode())

        assert result is None


@pytest.mark.parametrize(
    "mock_hdop, expected",
    [
        (0.0, True),
        (1.0, True),
        (2.0, True),
        (3.0, True),
        (4.0, True),
        (5.0, True),
        (5.1, False),
        (6.0, False),
        (7.0, False),
        (8.0, False),
        (9.0, False),
    ],
)
@patch("geolocator.gps_modules.neo_6m.serial.Serial")
def test_check_hdop_data(
    mock_serial: MagicMock,
    mock_hdop: float,
    expected: bool,
):
    neo_6m_gps_module = Neo6MGPSModule()

    # Test _check_hdop_data
    result = neo_6m_gps_module._check_hdop_data(mock_hdop)

    assert result == expected


@pytest.mark.parametrize(
    "mock_land_speed, expected",
    [
        (0.0, True),
        (50.0, True),
        (100.0, True),
        (150.0, True),
        (200.0, True),
        (200.1, False),
        (250.0, False),
        (300.0, False),
        (350.0, False),
        (400.0, False),
    ],
)
@patch("geolocator.gps_modules.neo_6m.serial.Serial")
def test_check_land_speed(
    mock_serial: MagicMock,
    mock_land_speed: float,
    expected: bool,
):
    neo_6m_gps_module = Neo6MGPSModule()

    # Test _check_land_speed
    result = neo_6m_gps_module._check_land_speed(mock_land_speed)

    assert result == expected
