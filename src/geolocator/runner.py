import argparse
import time
import datetime

from geolocator.displays import get_display, Display, DisplayType

from geolocator.gps_modules import get_gps_module, GPSModuleType
from geolocator.utils import update_system_datetime

UPDATE_TIME_INTERVAL = 60 * 5


class GeolocatorRunner:
    def __init__(self):
        self.last_update_time = None

    def run(self, display: Display, gps_module_type: str):
        """Run the geolocator application.

        Args:
            display (Display): The display to use
            gps_module_type (str): The GPS module to use
        """
        gps_module = get_gps_module(module_type=gps_module_type)

        display.startup_screen()

        time.sleep(3)

        display_count = 0

        while True:
            altitude_data = gps_module.get_altitude_data()

            if altitude_data:
                # Update the system time if the last update time was more than the
                # update time interval ago
                if self.update_time_has_expired():
                    update_system_datetime(altitude_data.local_time)
                    self.last_update_time = datetime.datetime.now()

                if display_count == 0:
                    display.cleanup()
                    display_count += 1
                display.render(altitude_data)

    def update_time_has_expired(self) -> bool:
        """Check if the last update time was more than the update time interval ago. Will return True
        if the system time has never been updated.

        Returns:
            bool: True if the last update time was more than the update time interval ago, False otherwise
        """
        if not self.last_update_time:
            return True

        return datetime.datetime.now() - self.last_update_time > datetime.timedelta(
            seconds=UPDATE_TIME_INTERVAL
        )


def cli():
    """Run the geolocator application from the command line. Parses the command line arguments and runs the application."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--display",
        type=str,
        help="The display type to use",
        default=DisplayType.EMULATOR.value,
        choices=[display_type.value for display_type in DisplayType],
    )

    parser.add_argument(
        "--gps",
        type=str,
        help="The GPS module to use",
        default=GPSModuleType.FAKE.value,
        choices=[gps_type.value for gps_type in GPSModuleType],
    )

    args = parser.parse_args()

    display_type = args.display

    gps_type = args.gps

    display = get_display(display_type=display_type)

    try:
        GeolocatorRunner().run(display, gps_type)
        display.cleanup()
    finally:
        display.cleanup()
