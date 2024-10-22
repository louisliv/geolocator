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
    def _get_text_size(self, text, font: ImageFont.FreeTypeFont):
        text_size = font.getbbox(text)

        return (text_size[2], text_size[3])

    def init_interface(self):
        return None

    def init_device(self, _device_type):
        return pygame(WIDTH, HEIGHT)

    def cleanup(self):
        pass
