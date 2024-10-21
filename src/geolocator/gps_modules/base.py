from typing import Optional
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from geolocator.client import get_closest_city, get_sql_engine
from geolocator.models.city import City

SQLITE_FILE = "geolocator.db"


class GPSData:
    def __init__(
        self,
        latitude: float,
        longitude: float,
        gps_time: str,
        closest_city_name: str,
        timestamp: float,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.gps_time = gps_time
        self.closest_city_name = closest_city_name
        self.timestamp = timestamp

    def __repr__(self):
        return f"<GPSData(latitude={self.latitude}, longitude={self.longitude}, gps_time={self.gps_time}, closest_city_name={self.closest_city_name})>"


class AltitudeData:
    def __init__(
        self,
        altitude: float,
        altitude_units: str,
    ):
        self.altitude = altitude
        self.altitude_units = altitude_units

    def __repr__(self):
        return f"<AltitudeData(altitude={self.altitude}, altitude_units={self.altitude_units})>"


class GPSCompleteData:
    def __init__(
        self,
        latitude: float,
        longitude: float,
        gps_time: str,
        closest_city_name: str,
        timestamp: float,
        altitude: float,
        altitude_units: str,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.gps_time = gps_time
        self.closest_city_name = closest_city_name
        self.timestamp = timestamp
        self.altitude = altitude
        self.altitude_units = altitude_units


class GPSModule:
    def read(self) -> GPSData:
        raise NotImplementedError

    def get_altitude_data(self) -> GPSCompleteData:
        raise NotImplementedError

    def get_current_city(self, lat, lng) -> Optional[City]:

        engine = get_sql_engine()
        with Session(engine) as session:
            return get_closest_city(session, lat, lng)
