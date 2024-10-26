from typing import Optional
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from geolocator.client import get_closest_city, get_sql_engine
from geolocator.models.city import City

SQLITE_FILE = "geolocator.db"


class GPSData:
    """A class to represent GPS data. This class is meant to be subclassed by other classes that provide more specific GPS data.

    Class Attributes:
        latitude (float): The latitude of the GPS data.
        longitude (float): The longitude of the GPS data.
        gps_time (str): The time the GPS data was recorded.
        closest_city_name (str): The name of the closest city to the GPS data.
        timestamp (float): The timestamp of the GPS data.
        closest_city_timezone (str): The timezone of the closest city to the GPS data.
        local_time (str): The local time of the closest city to the GPS data
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        gps_time: str,
        closest_city_name: str,
        closest_city_timezone: str,
        local_time: str,
        timestamp: float,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.gps_time = gps_time
        self.closest_city_name = closest_city_name
        self.timestamp = timestamp
        self.closest_city_timezone = closest_city_timezone
        self.local_time = local_time

    def __repr__(self):
        return f"<GPSData(latitude={self.latitude}, longitude={self.longitude}, gps_time={self.gps_time}, closest_city_name={self.closest_city_name})>"


class GPSCompleteData(GPSData):
    """A class to represent GPS data that includes altitude information.

    Class Attributes:
        latitude (float): The latitude of the GPS data.
        longitude (float): The longitude of the GPS data.
        gps_time (str): The time the GPS data was recorded.
        closest_city_name (str): The name of the closest city to the GPS data.
        timestamp (float): The timestamp of the GPS data.
        closest_city_timezone (str): The timezone of the closest city to the GPS data.
        local_time (str): The local time of the closest city to the GPS data
        altitude (float): The altitude of the GPS data.
        altitude_units (str): The units of the altitude data.
    """

    def __init__(
        self,
        altitude: float,
        altitude_units: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.altitude = altitude
        self.altitude_units = altitude_units


class GPSModule:
    def read(self) -> GPSData:
        """Read GPS data from the GPS module and return it as a GPSData object.

        Raises:
            NotImplementedError: This method must be implemented by the subclass

        Returns:
            GPSData: The GPS data read from the GPS module
        """
        raise NotImplementedError

    def get_altitude_data(self) -> GPSCompleteData:
        """Get the GPS data from the GPS module, including altitude data.

        Raises:
            NotImplementedError: This method must be implemented by the subclass

        Returns:
            GPSCompleteData: The GPS data read from the GPS module, including altitude data
        """
        raise NotImplementedError

    def get_current_city(self, lat, lng) -> Optional[City]:
        """Get the closest city to the given latitude and longitude via the SQL database."""
        engine = get_sql_engine()
        with Session(engine) as session:
            return get_closest_city(session, lat, lng)
