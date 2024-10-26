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


def file_logger(message: str, file_name: str = "geolocator_logs.txt"):
    """Log the message to a file

    Args:
        message (str): The message to log
        file_name (str, optional): The name of the file to log to. Defaults to "geolocator_logs.txt".
    """
    # open/create and append log message to file
    with open(file_name, "a") as file:
        file.write(message)
