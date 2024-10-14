from datetime import datetime

import pytz

# try to import serial. raise ImportError if it fails
try:
    import serial # type: ignore
except ImportError:
    raise ImportError("Please install pyserial library. Run 'pip install pyserial'")

import pynmea2
from pynmea2 import GGA

from geolocator.gps_modules.base import GPSModule, GPSData

DEV_PORT = "/dev/ttyAMA0"

DEFAULT_GPS_DATA = GPSData(
    latitude=0.0,
    longitude=0.0,
    gps_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    closest_city_name="San Francisco, CA",
    timestamp=datetime.now().timestamp()
)

class Neo6MGPSModule(GPSModule):
    def __init__(self):
        self.ser = serial.Serial(DEV_PORT, 9600, timeout=0.5)
        self.nmea_stream_reader = pynmea2.NMEAStreamReader()
        
    def read(self) -> GPSData:
        new_data = self.ser.readline()
        
        if new_data and new_data[0:6] == "$GPRMC":
            new_msg: GGA = pynmea2.parse(new_data)
            
            if not new_msg:
                return DEFAULT_GPS_DATA
            
            lat = new_msg.latitude
            lng = new_msg.longitude
            
            current_city = self.get_current_city(lat, lng)
            
            timestamp_epoch = new_msg.timestamp.timestamp()
            
            timezone = pytz.timezone(current_city.timezone)
            
            timestamp = datetime.fromtimestamp(timestamp_epoch, tz=timezone).strftime("%Y-%m-%d %H:%M:%S")
            
            return GPSData(
                latitude=lat,
                longitude=lng,
                gps_time=timestamp,
                closest_city_name=f"{current_city.name}, {current_city.state_id}",
                timestamp=timestamp_epoch
            )
            
            
        return DEFAULT_GPS_DATA
