from datetime import datetime, time
from typing import Optional, Union

import pytz

# try to import serial. raise ImportError if it fails
try:
    import serial  # type: ignore
except ImportError:
    raise ImportError("Please install pyserial library. Run 'pip install pyserial'")

import pynmea2
from pynmea2 import GGA, RMC

from geolocator.gps_modules.base import GPSModule, GPSData, GPSCompleteData

DEV_PORT = "/dev/ttyUSB0"


class Neo6MGPSModule(GPSModule):
    def __init__(self):
        self.ser = serial.Serial(DEV_PORT, 9600, timeout=0.5)
        self.nmea_stream_reader = pynmea2.NMEAStreamReader()

    def read(self) -> Optional[GPSData]:
        """Read the GPS data from the NEO-6M GPS module.

        Returns:
            Optional[GPSData]: The GPS data read from the NEO-6M GPS module. Returns None if the data is not reliable.
        """
        new_data = self.ser.readline().decode()

        if new_data and new_data[0:6] == "$GPRMC":
            return self._handle_rmc_data(new_data)

    def get_altitude_data(self) -> Optional[GPSCompleteData]:
        """Get the GPS data from the NEO-6M GPS module, including altitude data.

        Returns:
            Optional[GPSCompleteData]: The GPS data read from the NEO-6M GPS module. Returns None if the data is not reliable.
        """
        new_data = self.ser.readline().decode()

        if new_data and (new_data[0:6] == "$GPGGA" or new_data[0:6] == "$GNGGA"):
            return self._handle_gga_data(new_data)

    def _parse_gps_data(self, data: Union[RMC, GGA]) -> Optional[GPSData]:
        """Parse the GPS data from the NEO-6M GPS module.

        Args:
            data (Union[RMC, GGA]): The GPS data to parse

        Returns:
            Optional[GPSData]: The parsed GPS data
        """
        lat = data.latitude
        lng = data.longitude

        current_city = self.get_current_city(lat, lng)
        timestamp_epoch: time = data.timestamp  # this is a UTC time object

        timezone = pytz.timezone(current_city.timezone)

        # convert the utc time to the local time
        utc_datetime = datetime.combine(
            datetime.today(), timestamp_epoch, tzinfo=pytz.utc
        )
        epoch = utc_datetime.timestamp()
        timestamp = datetime.fromtimestamp(epoch, timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return GPSData(
            latitude=lat,
            longitude=lng,
            gps_time=timestamp,
            closest_city_name=f"{current_city.name}, {current_city.state_id}",
            closest_city_timezone=current_city.timezone,
            local_time=timestamp,
            timestamp=timestamp_epoch,
        )

    def _handle_rmc_data(self, rmc_data: str) -> Optional[GPSData]:
        """Handle the RMC data from the NEO-6M GPS module.

        Args:
            rmc_data (str): The NMEA sentence containing the RMC data

        Returns:
            Optional[GPSData]: The GPS data parsed from the RMC data. Returns None if the data cannot be parsed.
        """
        try:
            new_msg: RMC = pynmea2.parse(rmc_data)
        except:
            return None

        if not new_msg:
            return None

        # check if the gps data is reliable
        if not self._check_land_speed(new_msg.spd_over_grnd):
            return None

        gps_data = self._parse_gps_data(new_msg)

        return gps_data

    def _handle_gga_data(self, gga_data: str) -> Optional[GPSCompleteData]:
        """Handle the GGA data from the NEO-6M GPS module.

        Args:
            gga_data (str): The NMEA sentence containing the GGA data

        Returns:
            Optional[GPSCompleteData]: The GPS data parsed from the GGA data. Returns None if the data cannot be parsed.
        """
        try:
            new_msg: GGA = pynmea2.parse(gga_data)
        except:
            return None

        if not new_msg:
            return None

        # check if the gps data is reliable
        if not self._check_hdop_data(new_msg.horizontal_dil):
            return None

        altitude = new_msg.altitude
        altitude_units = new_msg.altitude_units

        gps_data = self._parse_gps_data(new_msg)

        return GPSCompleteData(
            latitude=gps_data.latitude,
            longitude=gps_data.longitude,
            gps_time=gps_data.gps_time,
            closest_city_name=gps_data.closest_city_name,
            timestamp=gps_data.timestamp,
            closest_city_timezone=gps_data.closest_city_timezone,
            local_time=gps_data.local_time,
            altitude=altitude,
            altitude_units=altitude_units,
        )

    def _check_hdop_data(self, hdop) -> bool:
        """Horizonal Dilution of Precision (HDOP) is a measure of the
        precision of the GPS data. If the value is greater than 5, the
        gps data is not reliable and should be discarded.

        Args:
            hdop (str): The HDOP value from the GPS data

        Returns:
            bool: True if the HDOP value is less than 5, False otherwise
        """
        try:
            hdop = float(hdop)
        except:
            return False

        if hdop > 5:
            return False

        return True

    def _check_land_speed(self, speed) -> bool:
        """Check if the land speed is greater than 200 knots. If it is,
        the data is not reliable and should be discarded.

        Args:
            speed (str): The land speed from the GPS data (in knots)

        Returns:
            bool: True if the land speed is less than 200 knots, False otherwise
        """

        try:
            speed = float(speed)
        except:
            return False

        if speed > 200:
            return False

        return True
