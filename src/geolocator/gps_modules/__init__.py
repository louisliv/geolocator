from geolocator.gps_modules.base import GPSModule, GPSData


def get_gps_module() -> GPSModule:
    # Return the appropriate GPS module based on the environment

    # try to import serial. Use the FakeGPSModule if it fails
    try:
        import serial # type: ignore
    except ImportError:
        from geolocator.gps_modules.fake import FakeGPSModule
        return FakeGPSModule()

    return init_real_gps()


def init_real_gps():
    from geolocator.gps_modules.neo_6m import Neo6MGPSModule
    return Neo6MGPSModule()
