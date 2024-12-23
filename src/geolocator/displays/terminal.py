from datetime import datetime
import curses
from typing import Optional

from pyfiglet import Figlet

from geolocator.displays.base import Display
from geolocator.gps_modules import GPSData, GPSCompleteData


class TerminalDisplay(Display):
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

        self.stdscr.keypad(1)

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, 11, -1)  # AMBER
        curses.init_pair(2, 12, -1)  # BLUE

        self.city_window = curses.newwin(1, 50, 0, 0)
        self.time_window = curses.newwin(10, 150, 1, 15)
        self.gps_window = curses.newwin(3, 10, 1, 0)
        self.altitude_window = curses.newwin(1, 10, 5, 0)

    def render(self, gps_data: GPSData):
        """Render the GPS data on the terminal. This includes the city name, current time, gps coordinates, and altitude data."""
        self.write_city_data_to_terminal(gps_data.closest_city_name)
        self.write_time_to_terminal(gps_data.gps_time)
        self.write_gps_data_to_terminal(gps_data)

    def write_time_to_terminal(self, gps_time: str):
        """Write the time to the terminal using curses.

        Args:
            gps_time (str): The GPS time in the format "YYYY-MM-DD HH:MM:SS"
        """
        self.time_window.clear()
        # Write the time in HH:MM:SS format to the terminal using curses

        try:
            datetime_obj = datetime.strptime(gps_time, "%Y-%m-%d %H:%M:%S")

            time_str = datetime_obj.strftime("%-I:%M %p")
        except:
            time_str = "00:00"

        figlet = Figlet()

        time_string_ascii = figlet.renderText(time_str)

        for i, line in enumerate(time_string_ascii.split("\n")):
            self.time_window.addstr(i, 0, line, curses.color_pair(2))

        self.time_window.refresh()

    def write_gps_data_to_terminal(self, gps_data: GPSData):
        """Write the latitude and longitude to the terminal using curses

        Args:
            gps_data (GPSData): The GPS data containing the latitude and longitude
        """
        latitude = gps_data.latitude
        longitude = gps_data.longitude
        self.gps_window.clear()
        self.gps_window.addstr(1, 0, f"{round(latitude, 4)}", curses.color_pair(2))
        self.gps_window.addstr(2, 0, f"{round(longitude, 4)}", curses.color_pair(2))

        self.gps_window.refresh()

    def write_altitude_to_terminal(self, altitude_data: GPSCompleteData):
        """Write the altitude to the terminal using curses

        Args:
            altitude_data (GPSCompleteData): The altitude data to display
        """
        altitude = altitude_data.altitude
        altitude_units = altitude_data.altitude_units
        self.altitude_window.clear()
        self.altitude_window.addstr(
            0, 0, f"{altitude} {altitude_units}", curses.color_pair(2)
        )
        self.altitude_window.refresh()

    def write_city_data_to_terminal(self, city: str):
        """Write the city data to the terminal using curses

        Args:
            city (str): The city name to display
        """
        self.city_window.clear()
        self.city_window.addstr(0, 0, city, curses.color_pair(1))
        self.city_window.refresh()

    def cleanup(self):
        """Cleanup the terminal display"""
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
