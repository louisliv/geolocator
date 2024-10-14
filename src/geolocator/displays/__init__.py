from geolocator.displays.base import Display


def get_display() -> Display:
    # Return the appropriate display based on the environment

    from geolocator.displays.terminal import TerminalDisplay
    
    return TerminalDisplay()
