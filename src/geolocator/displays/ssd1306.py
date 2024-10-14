from datetime import datetime

import framebuf

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

from geolocator.gps_modules import GPSData
from geolocator.displays.base import Display
from geolocator.displays.constants import TACO, NUMS_502210, NUMS_642, NUMS_764

SCL_PIN = 17
SDA_PIN = 16


class SSD1306Display(Display):
    def __init__(self):
        self.i2c_dev = self.init_i2c(SCL_PIN, SDA_PIN)
        self.oled = SSD1306_I2C(128, 64, self.i2c_dev)

    def render(self, gps_data: GPSData):
        closest_city = gps_data.closest_city_name

        gps_datetime = datetime.strptime(gps_data.gps_time, "%Y-%m-%d %H:%M:%S")
        gps_hours = gps_datetime.hour
        gps_minutes = gps_datetime.minute

        gps_latitute = gps_data.latitude
        gps_longitude = gps_data.longitude

        self.display_clock(gps_hours, gps_minutes)
        self.display_home_clock(gps_hours, gps_minutes)
        self.display_gps_filler()
        self.display_text([closest_city])
        self.display_coordinates(gps_latitute, gps_longitude)

    def display_text(self, text_list):
        for i, line in enumerate(text_list):
            self.oled.fill_rect(0, i * 10, 128, 10, 0)
            self.oled.text(line, 0, i * 10)
        self.oled.show()

    def display_taco(self):
        self.oled.fill_rect(0, 10, 28, 28, 0)
        fb = framebuf.FrameBuffer(TACO, 28, 28, framebuf.MONO_HLSB)
        self.oled.blit(fb, 0, 10)
        self.oled.show()

    def display_clock(self, hours, minutes):
        hww = [50, 22, 10]
        x = 0
        self.oled.fill_rect(30, 64 - hww[0], 4 * hww[1] + hww[2], hww[0], 0)

        hours = hours % 12 if hours != 12 else 12
        for it, t in enumerate(f"{hours: >2}{minutes:02}"):
            if t != " ":
                buffer = NUMS_502210[int(t)]
                fb = framebuf.FrameBuffer(buffer, hww[1], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, 30 + x, 64 - hww[0])
            x = x + hww[1]
            if it == 1:
                buffer = NUMS_502210[-1]
                fb = framebuf.FrameBuffer(buffer, hww[2], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, 30 + x, 64 - hww[0])
                x = x + hww[2]
        self.oled.show()

    def display_home_clock(self, hours, minutes):
        hww = [7, 6, 4]
        hours_at_home = hours - 5
        hours_at_home = hours % 24 if hours != 24 else 24
        hours_elsewhere = hours_elsewhere + 2
        hours_elsewhere = hours_elsewhere % 24 if hours_elsewhere != 24 else 24
        x = 0
        self.oled.fill_rect(
            0, 64 - hww[0] * 2 - 2, 4 * hww[1] + hww[2], 2 * hww[0] + 2, 0
        )
        for it, t in enumerate(f"{hours_elsewhere: >2}{MM:02}"):
            if t != " ":
                buffer = NUMS_764[int(t)]
                fb = framebuf.FrameBuffer(buffer, hww[1], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, x, 64 - hww[0])
            x = x + hww[1]
            if it == 1:
                buffer = NUMS_764[-1]
                fb = framebuf.FrameBuffer(buffer, hww[2], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, x, 64 - hww[0])
                x = x + hww[2]
        x = 0
        for it, t in enumerate(f"{hours_at_home: >2}{minutes:02}"):
            if t != " ":
                buffer = NUMS_764[int(t)]
                fb = framebuf.FrameBuffer(buffer, hww[1], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, x, 64 - hww[0] * 2 - 2)
            x = x + hww[1]
            if it == 1:
                buffer = NUMS_764[-1]
                fb = framebuf.FrameBuffer(buffer, hww[2], hww[0], framebuf.MONO_HLSB)
                self.oled.blit(fb, x, 64 - hww[0] * 2 - 2)
                x = x + hww[2]
        self.oled.show()

    def display_coordinates(self, lat, lon):
        hww = [6, 4, 2]
        for i, line in enumerate([str(lat), str(lon)]):
            x = 0
            line = line.replace("-", "")
            self.oled.fill_rect(0, 64 - hww[0] * (6 - i) + i, 5 * hww[1], hww[0], 0)
            for it, t in enumerate(line):
                if t != ".":
                    buffer = NUMS_642[int(t)]
                    fb = framebuf.FrameBuffer(
                        buffer, hww[1], hww[0], framebuf.MONO_HLSB
                    )
                    self.oled.blit(fb, x, 64 - (hww[0]) * (6 - i) + i)
                    x = x + hww[1]
                if it == 1:
                    buffer = NUMS_642[-1]
                    fb = framebuf.FrameBuffer(
                        buffer, hww[2], hww[0], framebuf.MONO_HLSB
                    )
                    self.oled.blit(fb, x, 64 - (hww[0]) * (6 - i) + i)
                    x = x + hww[2]
        self.oled.show()

    def display_gps_filler(self):
        self.oled.fill_rect(0, 10, 28, 34, 0)
        self.oled.show()

    def init_i2c(scl_pin, sda_pin):
        i2c_dev = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=200000)
        i2c_addr = [hex(ii) for ii in i2c_dev.scan()]
        return i2c_dev

    def cleanup(self):
        pass
