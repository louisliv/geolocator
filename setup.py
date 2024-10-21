from setuptools import setup, find_packages

setup(
    name='geolocator',
    version='0.3.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'geolocator': ['geolocator.db', 'fonts/*'],
    },
    include_package_data=True,
    install_requires=[
        'pyfiglet',
        'SQLAlchemy',
        'pytz',
        'Adafruit-SSD1306',
        'adafruit-circuitpython-framebuf',
        'adafruit-circuitpython-ssd1306',
        'pynmea2',
    ],
    entry_points={
        'console_scripts': [
            'geolocator=geolocator.cli:main',
        ],
    },
)
