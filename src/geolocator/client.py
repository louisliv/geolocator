from typing import Optional
import math
from pathlib import Path

from sqlalchemy import func, create_engine, Engine
from sqlalchemy.orm import Session

from geolocator.models.city import City

SQLITE_FILE = "geolocator.db"


# Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def get_closest_city(session: Session, lat: float, lng: float) -> Optional[City]:
    """Get the closest city to the given latitude and longitude based on the city data in the database.

    Args:
        session (Session): The SQLAlchemy session to use to query the database.
        lat (float): The latitude of the location.
        lng (float): The longitude of the location.

    Returns:
        Optional[City]: The closest city to the given latitude and longitude.
    """
    closest_city = (
        session.query(City)
        .order_by(func.abs(City.lat - lat) + func.abs(City.lng - lng))
        .first()
    )
    return closest_city


def get_sql_engine() -> Engine:
    """Get the SQLAlchemy engine for the SQLite database.

    Returns:
        Engine: The SQLAlchemy engine for the SQLite database.
    """
    import geolocator

    db_location = Path(geolocator.__file__).parent / SQLITE_FILE
    return create_engine(f"sqlite:///{db_location}")
