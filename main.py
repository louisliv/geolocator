import time

from geolocator.displays import get_display, Display

from geolocator.gps_modules import get_gps_module


def main(display: Display):
    gps_module = get_gps_module()
    
    while True:
        gps_data = gps_module.read()
        display.render(gps_data)
        time.sleep(1)
    
if __name__ == '__main__':
    display = get_display()
    
    try:
        main(display)
        display.cleanup()
    except KeyboardInterrupt as e:
        display.cleanup()
        raise e
