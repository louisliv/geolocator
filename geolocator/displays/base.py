from geolocator.gps_modules import GPSData


class Display:
    def render(self, gps_data: GPSData):
        raise NotImplementedError
    
    def cleanup(self):
        raise NotImplementedError
