# geolocator


## Dev Environment

### Start virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies
```bash
python -m pip install -r requirements.txt
```

### Run dev environment from cli

This will run the emulator and display the data in the terminal using data retreived from http://localhost:5000.
```bash
cd src
python cli.py --display=emulator
```

If your have a NEO 6M GPS module connected to your computer, you can run the following command to get the GPS data:
```bash
cd src
python cli.py --display=emulator --gps=neo_6m
```

To run the app from cli with hot reloading:
```bash
cd src
watchmedo auto-restart -p "*.py" -R python -- cli.py --display=emulator --gps=neo_6m
```
