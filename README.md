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

### Install the package on the Raspberry Pi

Create a wheel file:
```bash
python setup.py bdist_wheel
```

Copy the wheel file to the Raspberry Pi:
```bash
scp dist/geolocator-0.<latest_version>.0-py3-none-any.whl pi@<ip_address>:~/
```

Install the wheel file on the Raspberry Pi:
```bash
ssh pi@<ip_address>
sudo pip3 install geolocator-0.<latest_version>.0-py3-none-any.whl
```

### Run the app on the Raspberry Pi

```bash
sudo geolocator --display=oled --gps=neo_6m
```

### Run the app on the Raspberry Pi at startup

```bash
scp service_files/geolocator.service pi@<ip_address>:~/
ssh pi@<ip_address>
sudo mv geolocator.service /etc/systemd/system/
sudo systemctl enable geolocator
sudo systemctl start geolocator
```
