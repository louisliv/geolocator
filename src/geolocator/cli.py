import sys
import argparse

from geolocator.displays import get_display, Display, DisplayType

from geolocator.gps_modules import get_gps_module


def run(display: Display):
    gps_module = get_gps_module()

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
        default=DisplayType.TERMINAL.value,
        choices=[display_type.value for display_type in DisplayType]
    )

    args = parser.parse_args()

    display_type = args.display

    display = get_display(display_type=display_type)

    try:
        run(display)
        display.cleanup()
    finally:
        display.cleanup()


if __name__ == "__main__":
    main()
