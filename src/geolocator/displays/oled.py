from datetime import datetime
from pathlib import Path

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306, device
from luma.core.render import canvas, ImageDraw

from PIL import ImageFont

from geolocator.gps_modules import GPSCompleteData
from geolocator.displays.base import Display
import geolocator

WIDTH = 128
HEIGHT = 64
SSD1306_ADDR = 0x3C
FONT_FILE = "fonts/red_alert.ttf"
GEOLOCATOR_PATH = Path(geolocator.__file__).parent
FONT_FILE_PATH = GEOLOCATOR_PATH / FONT_FILE
CLOCK_FORMAT = "%-I:%M"
MAX_CITY_NAME_LENGTH = 17


class OLEDDisplay(Display):
    def __init__(self):
        self.i2c_dev = self.init_i2c()
        self.oled: device = ssd1306(self.i2c_dev)
        self.large_font = ImageFont.truetype(str(FONT_FILE_PATH), 48)
        self.small_font = ImageFont.truetype(str(FONT_FILE_PATH), 18)
        self.xs_font = ImageFont.truetype(str(FONT_FILE_PATH), 12)
        self.time_with_seconds_font = ImageFont.truetype(str(FONT_FILE_PATH), 36)

    def render_altitude(self, altitude_data):
        pass

    def display_altitude(self, altitude_data: GPSCompleteData, draw: ImageDraw):
        # Put the altitude data under the city name
        data_to_display = f"{altitude_data.altitude} {altitude_data.altitude_units}"

        # get y coordinate from the bounding box
        y_start = 15

        draw.text(
            (0, y_start),
            f"Alt: {data_to_display}",
            fill="white",
            font=self.xs_font,
        )

    def render(self, gps_data: GPSCompleteData):
        closest_city = gps_data.closest_city_name

        gps_datetime = datetime.strptime(gps_data.gps_time, "%Y-%m-%d %H:%M:%S")

        with canvas(self.oled) as draw:
            self.display_clock(gps_datetime, draw)
            self.display_city(closest_city, draw)
            self.display_altitude(gps_data, draw)

    def display_city(self, text: str, draw: ImageDraw):
        # Display the city name on the first line of the OLED display
        city_name = self._format_city_name(text)
        draw.text((0, 0), city_name, fill="white", font=self.small_font)

    def _format_city_name(self, city_name: str) -> str:
        # Format the city name to fit on the OLED display. If the city name is too long, we will truncate it
        # and add an ellipsis at the end

        if len(city_name) > MAX_CITY_NAME_LENGTH:
            city_name = city_name[: MAX_CITY_NAME_LENGTH - 3] + "..."

        return city_name

    def display_clock(self, gps_time: datetime, draw: ImageDraw):
        # Display the current time on the OLED display using a large font

        font_to_use = self.large_font

        time_to_display = gps_time.strftime(CLOCK_FORMAT)

        # We want to put the text at bottom right of the display, so we need to calculate the x and y coordinates
        bounding_box = self.oled.bounding_box
        width = bounding_box[2] - bounding_box[0]
        text_width = self._get_text_size(time_to_display, font_to_use)[0]
        x = width - text_width

        # get y
        height = bounding_box[3] - bounding_box[1]
        text_height = self._get_text_size(time_to_display, font_to_use)[1]
        y = height - text_height

        draw.text((x, y), time_to_display, fill="white", font=font_to_use)

    def _get_text_size(self, text: str, font: ImageFont) -> tuple:
        return font.getsize(text)

    def init_i2c(self):
        i2c_dev = i2c(port=1, address=SSD1306_ADDR)
        return i2c_dev

    def cleanup(self):
        self.oled.clear()
