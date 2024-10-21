from geolocator.displays.base import Display


def get_display() -> Display:
    # Return the appropriate display based on the environment
    from geolocator.displays.terminal import TerminalDisplay

    try:
        from geolocator.displays.ssd1306 import SSD1306Display
        return SSD1306Display()
    except ImportError:
        return TerminalDisplay()
