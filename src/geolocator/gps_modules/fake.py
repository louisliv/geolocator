from datetime import datetime
from random import randint
import pytz

import requests

from geolocator.gps_modules.base import GPSModule, GPSCompleteData
from geolocator.client import get_sql_engine
from geolocator.models.city import City

from sqlalchemy.orm import Session

SQLITE_FILE = "geolocator.db"

# Atlanta, GA
FAKE_LAT = 33.7490
FAKE_LNG = -84.3880


class FakeGPSModule(GPSModule):
    def __init__(self, randomize=False):
        self.random_city_used_count = 0
        self.random_city = None
        self.randomize = randomize

        super().__init__()

    def read(self) -> GPSCompleteData:
        gps_data = self.retreive_fake_gps_data()

        latitude = gps_data["latitude"]
        longitude = gps_data["longitude"]

        current_city = self.get_current_city(latitude, longitude)
        timezone = pytz.timezone(current_city.timezone)

        date_time_from_gps = datetime.fromtimestamp(gps_data["gps_time"], tz=timezone)
        timestamp = date_time_from_gps.strftime("%Y-%m-%d %H:%M:%S")

        return GPSCompleteData(
            latitude=latitude,
            longitude=longitude,
            gps_time=timestamp,
            closest_city_name=f"{current_city.name}, {current_city.state_id}",
            timestamp=gps_data["gps_time"],
            altitude=gps_data["altitude"],
            altitude_units=gps_data["altitude_units"],
            closest_city_timezone=current_city.timezone,
            local_time=timestamp,
        )

    def retreive_fake_gps_data(self):
        try:
            response = requests.get("http://localhost:5000/get_geo_data")

            data = response.json()
        except:
            data = None

        if not data:
            if (
                not self.random_city or self.random_city_used_count == 200
            ) and self.randomize:
                self.random_city = self.get_random_city()
                self.random_city_used_count = 0

            self.random_city_used_count += 1

            return {
                "latitude": self.random_city.lat if self.randomize else FAKE_LAT,
                "longitude": self.random_city.lng if self.randomize else FAKE_LNG,
                "altitude": 100,
                "altitude_units": "m",
                "gps_time": datetime.now(pytz.utc).timestamp(),
            }

        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "gps_time": data["timestamp"],
            "altitude": data.get("altitude", 0.0),
            "altitude_units": data.get("altitude_units", "m"),
        }

    def get_altitude_data(self):
        return self.read()

    def get_random_city(self):
        engine = get_sql_engine()
        with Session(engine) as session:
            # get all cities
            cities = session.query(City).all()

            cities_count = len(cities)

            random_index = randint(0, cities_count - 1)

            return cities[random_index]
