from geolocator.gps_modules import GPSData


class Display:
    def render(self, gps_data: GPSData):
        """Render the GPS data on the display.

        Args:
            gps_data (GPSData): The GPS data to render on the display

        Raises:
            NotImplementedError: This method must be implemented by the subclass
        """
        raise NotImplementedError

    def cleanup(self):
        """Cleanup the display. This method is optional and can be implemented by the subclass."""
        pass

    def startup_screen(self):
        """Display the startup screen. This method is optional and can be implemented by the subclass."""
        pass
