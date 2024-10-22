from datetime import datetime, time
from typing import Optional

import pytz

# try to import serial. raise ImportError if it fails
try:
    import serial  # type: ignore
except ImportError:
    raise ImportError("Please install pyserial library. Run 'pip install pyserial'")

import pynmea2
from pynmea2 import GGA, RMC

from geolocator.gps_modules.base import GPSModule, GPSData, GPSCompleteData
from geolocator.displays.utils import file_logger

DEV_PORT = "/dev/ttyUSB0"


class Neo6MGPSModule(GPSModule):
    def __init__(self):
        self.ser = serial.Serial(DEV_PORT, 9600, timeout=0.5)
        self.nmea_stream_reader = pynmea2.NMEAStreamReader()

    def read(self) -> Optional[GPSData]:
        new_data = self.ser.readline().decode()

        if new_data and new_data[0:6] == "$GPRMC":
            return self._handle_rmc_data(new_data)

    def get_altitude_data(self):
        new_data = self.ser.readline().decode()

        if new_data and (new_data[0:6] == "$GPGGA" or new_data[0:6] == "$GNGGA"):
            return self._handle_gga_data(new_data)

    def _parse_gps_data(self, data) -> Optional[GPSData]:
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
            timestamp=timestamp_epoch,
        )

    def _handle_rmc_data(self, rmc_data) -> Optional[GPSData]:
        try:
            new_msg: RMC = pynmea2.parse(rmc_data)
        except:
            return None

        if not new_msg:
            return None

        gps_data = self._parse_gps_data(new_msg)

        return gps_data

    def _handle_gga_data(self, gga_data) -> Optional[GPSCompleteData]:
        try:
            new_msg: GGA = pynmea2.parse(gga_data)
        except:
            return None

        if not new_msg:
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
            altitude=altitude,
            altitude_units=altitude_units,
        )
