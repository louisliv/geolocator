import enum
import logging
from typing import Optional

from geolocator.displays.base import Display


class DisplayType(enum.Enum):
    TERMINAL = "terminal"
    OLED = "oled"
    WAVESHARE = "waveshare"
    EMULATOR = "emulator"


def get_display(display_type: Optional[str] = DisplayType.TERMINAL.value) -> Display:
    """Return the display object based on the display type

    Args:
        display_type (Optional[str], optional): The display type. Defaults to DisplayType.TERMINAL.value.

    Returns:
        Display: The display object
    """
    from geolocator.displays.terminal import TerminalDisplay

    try:
        if display_type == DisplayType.OLED.value:
            from geolocator.displays.oled import OLEDDisplay

            return OLEDDisplay()
        elif display_type == DisplayType.EMULATOR.value:
            from geolocator.displays.emulator import EmulatorDisplay

            return EmulatorDisplay()
    except:
        logging.exception("Could not import the display. Falling back to TerminalDisplay")
        return TerminalDisplay()

    return TerminalDisplay()
