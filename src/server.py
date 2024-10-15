from flask import Flask, jsonify, render_template

from geolocator.gps_modules import GPSData, get_gps_module

geo_module = get_gps_module()

app = Flask(__name__)


@app.route("/gps_data", methods=["GET"])
def get_gps_data():
    gps_data: GPSData = geo_module.read()
    return jsonify(
        {
            "latitude": gps_data.latitude,
            "longitude": gps_data.longitude,
            "altitude": gps_data.altitude,
            "altitude_units": gps_data.altitude_units,
            "gps_time": gps_data.gps_time,
            "closest_city_name": gps_data.closest_city_name,
        }
    )


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)