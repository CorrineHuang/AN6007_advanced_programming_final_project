from flask import Flask, jsonify, request
from datetime import datetime
from zoneinfo import ZoneInfo
from meter_readings_generation import generate_meter_readings

# Define API
app = Flask("__name__")

# Helper function to find a product by ID
def find_meter(meter_id):
    return next((meter for meter in meter_readings if meter_readings["ID"] == meter_id), None)

# 1. main page
@app.route("/", methods = ["GET", "POST"])
def main():
    return jsonify({"message": "THIS API IS WORKING!"}), 200

# 2. Get a meter readings by meter ID
@app.route('/meter?id=<value>', methods=['GET'])
def get_meter(value):
    meter_readings = find_meter(value)
    if meter_readings:
        return jsonify(meter_id), 200
    return jsonify({"error": "Product not found"}), 404



if __name__ == "__main__":
    meter_id = "SG-METER-001"
    start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Singapore"))
    end_date = datetime.now(ZoneInfo("Asia/Singapore"))

    meter_readings = generate_meter_readings(meter_id, start_date, end_date)
    print(meter_readings)


    app.run()
