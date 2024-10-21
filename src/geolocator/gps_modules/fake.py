from datetime import datetime
import pytz

import requests

from geolocator.gps_modules.base import GPSModule, GPSCompleteData

FAKE_LAT = 37.7749
FAKE_LNG = -122.4194
SQLITE_FILE = "geolocator.db"


class FakeGPSModule(GPSModule):
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
        )

    def retreive_fake_gps_data(self):
        response = requests.get("http://localhost:5000/get_geo_data")

        data = response.json()

        if not data:
            return {
                "latitude": FAKE_LAT,
                "longitude": FAKE_LNG,
                "altitude": 0.0,
                "altitude_units": "m",
                "gps_time": datetime.now().timestamp(),
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
