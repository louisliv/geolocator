import enum
from typing import Optional

from geolocator.displays.base import Display


class DisplayType(enum.Enum):
    TERMINAL = "terminal"
    SSD1306 = "ssd1306"
    WAVESHARE = "waveshare"


def get_display(display_type: Optional[str] = DisplayType.TERMINAL.value) -> Display:
    # Return the appropriate display based on the environment
    from geolocator.displays.terminal import TerminalDisplay

    try:
        if display_type == DisplayType.SSD1306.value:
            from geolocator.displays.ssd1306 import SSD1306Display

            return SSD1306Display()
        elif display_type == DisplayType.WAVESHARE.value:
            from geolocator.displays.waveshare import WaveshareDisplay

            return WaveshareDisplay()
    except:
        return TerminalDisplay()

    return TerminalDisplay()
