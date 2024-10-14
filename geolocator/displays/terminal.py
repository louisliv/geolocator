from datetime import datetime
import curses

from pyfiglet import Figlet
import pytz

from geolocator.displays.base import Display
from geolocator.gps_modules import GPSData

HOME_TZ = "America/New_York"


class TerminalDisplay(Display):
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, 11, -1)  # AMBER
        curses.init_pair(2, 12, -1)  # BLUE

        self.city_window = curses.newwin(1, 50, 0, 0)
        self.time_window = curses.newwin(10, 150, 1, 15)
        self.gps_window = curses.newwin(10, 10, 1, 0)

    def render(self, gps_data: GPSData):
        self.write_city_data_to_terminal(gps_data.closest_city_name)
        self.write_time_to_terminal(gps_data.gps_time)
        self.write_gps_data_to_terminal(
            gps_data.latitude, gps_data.longitude, gps_data.timestamp
        )

    def write_time_to_terminal(self, gps_time: str):
        self.time_window.clear()
        # Write the time in HH:MM:SS format to the terminal using curses

        try:
            datetime_obj = datetime.strptime(gps_time, "%Y-%m-%d %H:%M:%S")

            time_str = datetime_obj.strftime("%H:%M:%S")

            figlet = Figlet()

            time_string_ascii = figlet.renderText(time_str)

            for i, line in enumerate(time_string_ascii.split("\n")):
                self.time_window.addstr(i, 0, line, curses.color_pair(2))
        except:
            self.time_window.addstr(0, 0, "Time Unavailable", curses.color_pair(2))
            self.time_window.addstr(
                1, 0, f"time from server: {gps_time}", curses.color_pair(2)
            )

        self.time_window.refresh()

    def write_gps_data_to_terminal(
        self, latitude: float, longitude: float, timestamp: float
    ):
        # Write the latitude and longitude to the terminal using curses
        self.gps_window.clear()
        self.gps_window.addstr(1, 0, f"{round(latitude, 4)}", curses.color_pair(2))
        self.gps_window.addstr(2, 0, f"{round(longitude, 4)}", curses.color_pair(2))

        home_tz = pytz.timezone(HOME_TZ)

        home_time = datetime.fromtimestamp(timestamp, tz=home_tz)
        home_time_str = home_time.strftime("%H:%M")

        self.gps_window.addstr(4, 0, home_time_str, curses.color_pair(2))

        self.gps_window.refresh()

    def write_city_data_to_terminal(self, city: str):
        # Write the city data to the terminal using curses
        self.city_window.clear()
        self.city_window.addstr(0, 0, city, curses.color_pair(1))
        self.city_window.refresh()

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
