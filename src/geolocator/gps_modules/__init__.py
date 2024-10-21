import enum
import logging

from geolocator.gps_modules.base import (
    GPSModule,
    GPSData,
    AltitudeData,
    GPSCompleteData,
)

class GPSModuleType(enum.Enum):
    FAKE = "fake"
    NEO_6M = "neo_6m"


def get_gps_module(module_type: str = GPSModuleType.FAKE.value) -> GPSModule:
    # Return the appropriate GPS module based on the environment

    if module_type == GPSModuleType.FAKE.value:
        return init_fake_gps()

    # try to import serial. Use the FakeGPSModule if it fails
    try:
        if module_type == GPSModuleType.NEO_6M.value:
            return init_real_gps()
    except ImportError:
        logging.error("Could not import serial. Falling back to FakeGPSModule")
        return init_fake_gps()

    return init_fake_gps()


def init_fake_gps():
    from geolocator.gps_modules.fake import FakeGPSModule

    return FakeGPSModule()


def init_real_gps():
    from geolocator.gps_modules.neo_6m import Neo6MGPSModule

    return Neo6MGPSModule()
