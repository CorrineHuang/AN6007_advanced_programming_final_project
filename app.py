from flask import Flask, jsonify, request
from datetime import datetime
from zoneinfo import ZoneInfo
from meter_readings_generation import generate_meter_readings

# Define API
app = Flask("__name__")

# 1. mian page
@app.route("/", methods = ["GET", "POST"])
def main():
    return

# 2. xxx
@app.route("/xxxx", methods = ["GET", "POST"])
def xxx():
    return




if __name__ == "__main__":
    meter_id = "SG-METER-001"
    start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Singapore"))
    end_date = datetime.now(ZoneInfo("Asia/Singapore"))

    meter_readings = generate_meter_readings(meter_id, start_date, end_date)
    # print(meter_readings)


    app.run()
