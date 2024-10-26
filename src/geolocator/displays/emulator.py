from typing import Tuple
from pathlib import Path

from luma.emulator.device import pygame
from PIL import ImageFont

from geolocator.displays.oled import OLEDDisplay
import geolocator

WIDTH = 128
HEIGHT = 64
SSD1306_ADDR = 0x3C
FONT_FILE = "fonts/red_alert.ttf"
FONT_FILE_PATH = Path(geolocator.__file__).parent / FONT_FILE
MAX_CITY_NAME_LENGTH = 17


class EmulatorDisplay(OLEDDisplay):
    def _get_text_size(self, text, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Get the size of the text based on the font.

        Args:
            text (str): The text to get the size of
            font (ImageFont.FreeTypeFont): The font to use for the text

        Returns:
            Tuple[int, int]: The size of the text as a tuple of width and height
        """
        text_size = font.getbbox(text)

        return (text_size[2], text_size[3])

    def init_interface(self):
        """Initialize the interface for the display. This is specific to the display type.

        This is not needed for the emulator display, so we return None.
        """
        return None

    def init_device(self, _device_type):
        """Initialize the device for the display. This is specific to the display type.

        For the emulator display, we return the pygame device with the mode set to "1".
        """
        return pygame(WIDTH, HEIGHT, mode="1")
