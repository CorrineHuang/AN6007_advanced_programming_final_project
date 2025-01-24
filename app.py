import sys
import os
from flask import Flask, jsonify, request
from datetime import datetime
from zoneinfo import ZoneInfo
from meter_readings_generation import generate_meter_readings

sys.path.append(os.getcwd())

# Define API
app = Flask("__name__")

# Helper function to find a product by ID
def find_meter(meter_id):
    return meter_readings[meter_id] if meter_id in meter_readings else None

# 1. main page
@app.route("/", methods = ["GET", "POST"])
def main():
    return jsonify({"message": "THIS API IS WORKING!"}), 200

# 2. Get a meter readings by meter ID
@app.route('/meter/<value>', methods=['GET'])
def get_meter(value):
    meter_readings = find_meter(value)
    if meter_readings:
        return jsonify([meter.__dict__ for meter in meter_readings]), 200
    return jsonify({"error": "Meter not found"}), 404



if __name__ == "__main__":
    meter_id = "999"
    # start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Singapore"))
    # end_date = datetime.now(ZoneInfo("Asia/Singapore"))

    meter_readings = generate_meter_readings(meter_id)
    print(meter_readings)


    app.run()