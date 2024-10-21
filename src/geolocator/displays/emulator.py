from pathlib import Path

from luma.emulator.device import pygame
from PIL import ImageFont

from geolocator.displays.ssd1306 import SSD1306Display
import geolocator

WIDTH = 128
HEIGHT = 64
SSD1306_ADDR = 0x3C
FONT_FILE = "fonts/red_alert.ttf"
FONT_FILE_PATH = Path(geolocator.__file__).parent / FONT_FILE
MAX_CITY_NAME_LENGTH = 17


class EmulatorDisplay(SSD1306Display):
    def __init__(self):
        self.oled = pygame(WIDTH, HEIGHT)
        self.large_font = ImageFont.truetype(str(FONT_FILE_PATH), 48)
        self.small_font = ImageFont.truetype(str(FONT_FILE_PATH), 18)
        self.xs_font = ImageFont.truetype(str(FONT_FILE_PATH), 12)
        self.time_with_seconds_font = ImageFont.truetype(str(FONT_FILE_PATH), 36)

    def _get_text_size(self, text, font: ImageFont.FreeTypeFont):
        text_size = font.getbbox(text)

        return (text_size[2], text_size[3])

    def cleanup(self):
        pass
