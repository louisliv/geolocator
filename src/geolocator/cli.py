from geolocator.displays import get_display, Display

from geolocator.gps_modules import get_gps_module


def run(display: Display):
    gps_module = get_gps_module()

    while True:
        altitude_data = gps_module.get_altitude_data()

        if altitude_data:
            display.render(altitude_data)


def main():
    display = get_display()

    try:
        run(display)
        display.cleanup()
    finally:
        display.cleanup()


if __name__ == "__main__":
    main()
