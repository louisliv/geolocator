from geolocator.displays.base import Display


def get_display() -> Display:
    # Return the appropriate display based on the environment
    from geolocator.displays.terminal import TerminalDisplay

    # Try to import the SSD1306 display. If it fails, return the TerminalDisplay
    try:
        from geolocator.displays.ssd1306 import SSD1306Display

        return SSD1306Display()
    except Exception:
        return TerminalDisplay()
