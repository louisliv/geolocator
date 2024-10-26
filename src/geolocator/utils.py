from typing import Union
from datetime import datetime
import io
import os
import logging


def is_raspberrypi() -> bool:
    """Check if the current device is a Raspberry Pi.

    Returns:
        bool: True if the current device is a Raspberry Pi, False otherwise
    """

    try:
        with io.open("/sys/firmware/devicetree/base/model", "r") as m:
            if "raspberry pi" in m.read().lower():
                return True
    except Exception:
        pass

    return False


def update_system_datetime(time_to_set: Union[datetime, str]):
    """Update the system date and time.

    Args:
        time_to_set (Union[datetime, str]): The time to set the system to. If a string is provided, it should be in the
            format "%Y-%m-%d %H:%M:%S".
    """
    # determine if we can update the time. This is determined by the CAN_UPDATE_TIME environment variable
    # or if the current device is a Raspberry Pi
    can_update_time = get_boolean_env_var("CAN_UPDATE_TIME") or is_raspberrypi()

    # Only update the time if we can update the time
    if not can_update_time:
        return

    # convert string time to datetime if it is a string. This will raise an exception if the string is not in the
    # correct format. Handle the exception and log the error
    try:
        if isinstance(time_to_set, str):
            time_to_set = datetime.strptime(time_to_set, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error(
            "Invalid time format. Time should be in the format 'YYYY-MM-DD HH:MM:SS'"
        )
        return

    time_str = time_to_set.strftime("%Y-%m-%d %H:%M:%S")

    try:
        import subprocess

        subprocess.run(["sudo", "date", "-s", time_str])
    except Exception:
        pass


def get_boolean_env_var(var_name: str, default: bool = False) -> bool:
    """Get a boolean environment variable.

    Args:
        var_name (str): The name of the environment variable
        default (bool): The default value to return if the environment variable is not set

    Returns:
        bool: The value of the environment variable if it is set, otherwise the default
    """

    value = os.getenv(var_name)
    if value is None:
        return default

    return value.lower() in ["true", "1", "yes", "y"]
