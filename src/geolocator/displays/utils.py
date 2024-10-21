import curses


def terminal_logger(message: str) -> None:
    """
    Log the message to the curses terminal
    """

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    stdscr.keypad(1)

    stdscr.addstr(20, 0, message)

    # clean up
    stdscr.keypad(0)
    curses.echo()


def file_logger(message: str):
    file_name = "geolocator_logs.txt"

    # open/create and append log message to file
    with open(file_name, "a") as file:
        file.write(message)
