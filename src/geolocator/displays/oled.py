from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path
import enum
import logging

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309, sh1106, ssd1306, device
from luma.core.render import canvas, ImageDraw

from PIL import ImageFont, Image

from geolocator.gps_modules import GPSCompleteData
from geolocator.displays.base import Display
import geolocator

WIDTH = 128
HEIGHT = 64
SSD1306_ADDR = 0x3C
FONT_FILE = "fonts/red_alert.ttf"
STARTUP_SCREEN_FILE = "images/startup_screen.png"
GEOLOCATOR_PATH = Path(geolocator.__file__).parent
STARTUP_SCREEN_PATH = GEOLOCATOR_PATH / STARTUP_SCREEN_FILE
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
            self.command(
                set_page_address, 0x00, 0x10
            )  # Only difference is the 0x00 here
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

    def render(self, gps_data: GPSCompleteData, time_to_show: datetime = None):
        """Display the GPS data on the OLED display. This includes the city name, current time, and altitude data.

        Args:
            gps_data (GPSCompleteData): The GPS data to display
            time_to_show (datetime, optional): The time to display. Defaults to None. If None, the current time will be used.
        """
        closest_city = gps_data.closest_city_name

        time_to_show = time_to_show or datetime.now()

        with canvas(self.oled) as draw:
            self.display_clock(time_to_show, draw)
            self.display_city(closest_city, draw)
            self.display_altitude(gps_data, draw)

    def display_altitude(self, altitude_data: GPSCompleteData, draw: ImageDraw):
        """Display the altitude data on the OLED display.

        Args:
            altitude_data (GPSCompleteData): The GPS data containing the altitude data
            draw (ImageDraw): The ImageDraw object to draw on the OLED display
        """
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

    def display_city(self, text: str, draw: ImageDraw):
        """Display the city name on the OLED display.

        Args:
            text (str): The city name to display
            draw (ImageDraw): The ImageDraw object to draw on the OLED display
        """
        # Display the city name on the first line of the OLED display
        city_name = self._format_city_name(text)
        draw.text((0, 0), city_name, fill="white", font=self.small_font)

    def _format_city_name(self, city_name: str) -> str:
        """Format the city name to fit on the OLED display. If the city name is too long, we will truncate it
        and add an ellipsis at the end.

        Args:
            city_name (str): The city name to format

        Returns:
            str: The formatted city name
        """
        if len(city_name) > MAX_CITY_NAME_LENGTH:
            city_name = city_name[: MAX_CITY_NAME_LENGTH - 3] + "..."

        return city_name

    def display_clock(self, time_to_show: datetime, draw: ImageDraw):
        """Display the current time on the OLED display using the large font.

        Args:
            time_to_show (datetime): The time to display
            draw (ImageDraw): The ImageDraw object to draw on the OLED display
        """

        font_to_use = self.large_font

        time_to_display = time_to_show.strftime(CLOCK_FORMAT)

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

    def _get_text_size(self, text: str, font: ImageFont) -> Tuple[int, int]:
        """Get the size of the text based on the font.

        Args:
            text (str): The text to get the size of
            font (ImageFont): The font to use for the text

        Returns:
            Tuple[int, int]: The size of the text as a tuple of width and height
        """
        return font.getsize(text)

    def init_interface(self):
        """Initialize the interface for the OLED display. This is specific to the display type.

        Returns:
            i2c: The I2C interface for the OLED display
        """
        interface = i2c(port=1, address=SSD1306_ADDR)
        return interface

    def init_device(self, device_type: str = Devices.SSD1306.value):
        """Initialize the device for the OLED display. This is specific to the display type.

        Args:
            device_type (str, optional): The device type to initialize. Defaults to Devices.SSD1306.value.

        Raises:
            ValueError: If an invalid device type is provided

        Returns:
            The specific device for the OLED display based on the device type provided.
        """
        # match the device type to the function and return the device
        device_function = DEVICE_FUNCTIONS.get(device_type.value)

        if not device_function:
            raise ValueError(f"Invalid device type: {device_type}")

        return device_function(self.interface)

    def cleanup(self):
        """Clear the OLED display."""
        self.oled.clear()

    def startup_screen(self):
        """Display the startup animation on the OLED display"""

        self.oled.clear()

        img_path = str(STARTUP_SCREEN_PATH)

        try:
            startup_screen = Image.open(img_path)
        except FileNotFoundError:
            logging.warning(f"Startup screen image not found at {img_path}")

        # We need to resize the image to fit the OLED display
        startup_screen = startup_screen.resize(
            (self.oled.width, self.oled.height)
        ).convert(self.oled.mode)

        # Display the image on the OLED display
        self.oled.display(startup_screen)
