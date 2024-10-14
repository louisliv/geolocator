from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from geolocator.client import get_closest_city
from geolocator.models.city import City

SQLITE_FILE = 'geolocator.db'


class GPSData:
    def __init__(self,
        latitude: float,
        longitude: float,
        gps_time: str,
        closest_city_name: str,
        timestamp: float
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.gps_time = gps_time
        self.closest_city_name = closest_city_name
        self.timestamp = timestamp
        
    def __repr__(self):
        return f"<GPSData(latitude={self.latitude}, longitude={self.longitude}, gps_time={self.gps_time}, closest_city_name={self.closest_city_name})>"


class GPSModule:
    def read(self) -> GPSData:
        raise NotImplementedError
    
    def get_current_city(self, lat, lng) -> Optional[City]:
        engine = create_engine(f'sqlite:///{SQLITE_FILE}')
        with Session(engine) as session:
            return get_closest_city(session, lat, lng)
