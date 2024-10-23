from typing import Optional
from datetime import datetime
from pathlib import Path
import enum

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309, sh1106, ssd1306, device
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


class SH1106Device(sh1106):
    def display(self, image):
        """
        Takes a 1-bit :py:mod:`PIL.Image` and dumps it to the SH1106
        OLED display.

        :param image: Image to display.
        :type image: :py:mod:`PIL.Image`
        """
        assert image.mode == self.mode
        assert image.size == self.size

        image = self.preprocess(image)

        set_page_address = 0xB0
        image_data = image.getdata()
        pixels_per_page = self.width * 8
        buf = bytearray(self.width)

        for y in range(0, int(self._pages * pixels_per_page), pixels_per_page):
            self.command(set_page_address, 0x00, 0x10) # Only difference is the 0x00 here
            set_page_address += 1
            offsets = [y + self.width * i for i in range(8)]

            for x in range(self.width):
                buf[x] = (
                    (image_data[x + offsets[0]] and 0x01)
                    | (image_data[x + offsets[1]] and 0x02)
                    | (image_data[x + offsets[2]] and 0x04)
                    | (image_data[x + offsets[3]] and 0x08)
                    | (image_data[x + offsets[4]] and 0x10)
                    | (image_data[x + offsets[5]] and 0x20)
                    | (image_data[x + offsets[6]] and 0x40)
                    | (image_data[x + offsets[7]] and 0x80)
                )

            self.data(list(buf))


DEVICE_FUNCTIONS = {
    "ssd1306": ssd1306,
    "ssd1309": ssd1309,
    "sh1106": SH1106Device,
}


class Devices(enum.Enum):
    SSD1306 = "ssd1306"
    SSD1309 = "ssd1309"
    SH1106 = "sh1106"


class OLEDDisplay(Display):
    def __init__(self, device_type: Optional[Devices] = Devices.SH1106):
        self.interface = self.init_interface()
        self.oled: device = self.init_device(device_type)
        self.large_font = ImageFont.truetype(str(FONT_FILE_PATH), 48)
        self.small_font = ImageFont.truetype(str(FONT_FILE_PATH), 18)
        self.xs_font = ImageFont.truetype(str(FONT_FILE_PATH), 12)
        self.time_with_seconds_font = ImageFont.truetype(str(FONT_FILE_PATH), 36)
        self.oled.clear()

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

    def init_interface(self):
        interface = i2c(port=1, address=SSD1306_ADDR)
        return interface

    def init_device(self, device_type: str = Devices.SSD1306.value):
        # match the device type to the function and return the device
        device_function = DEVICE_FUNCTIONS.get(device_type.value)

        if not device_function:
            raise ValueError(f"Invalid device type: {device_type}")

        return device_function(self.interface)

    def cleanup(self):
        self.oled.clear()
