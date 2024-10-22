import argparse

from geolocator.displays import get_display, Display, DisplayType

from geolocator.gps_modules import get_gps_module, GPSModuleType


def run(display: Display, gps_module_type: str):
    gps_module = get_gps_module(module_type=gps_module_type)

    while True:
        altitude_data = gps_module.get_altitude_data()

        if altitude_data:
            display.render(altitude_data)


def main():
    # get the system arguments
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
        run(display, gps_type)
        display.cleanup()
    finally:
        display.cleanup()


if __name__ == "__main__":
    main()
