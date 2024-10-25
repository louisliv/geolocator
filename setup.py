from setuptools import setup, find_packages

setup(
    name='geolocator',
    version='0.3.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'geolocator': ['geolocator.db', 'fonts/*', 'images/*'],
    },
    include_package_data=True,
    install_requires=[
        'pyfiglet',
        'SQLAlchemy',
        'pytz',
        'luma.oled',
        'luma.core',
        'pynmea2',
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'geolocator=geolocator.main:main',
        ],
    },
)
