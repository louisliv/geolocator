from geolocator.gps_modules import GPSData, AltitudeData


class Display:
    def render(self, gps_data: GPSData):
        raise NotImplementedError

    def render_altitude(self, altitude_data: AltitudeData):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError
