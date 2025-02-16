# from datetime import datetime
import os
import re
# import random
# import pandas as pd
from flask import Flask, json, request, jsonify,render_template
from http import HTTPStatus
import json
import csv
from models.electricity_account import ElectricityAccount
from models.meter_reading import MeterReading
from utils import save_to_half_hourly_csv, calculate_daily_usage, calculate_monthly_usage

app = Flask(__name__)
file_path = os.path.join(os.getcwd(), 'archived_data', 'electricity_accounts.json')

# Load existing accounts
def load_electricity_accounts_from_file():
    """Load all meter accounts from file"""
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump([], file)
        return []

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return [ElectricityAccount.from_dict(account) for account in data]
    except json.JSONDecodeError:
        return []

# Save a new meter to the file
def save_electricity_accounts_to_file(electricity_account: ElectricityAccount):
    """Save a new meter to the file"""
    # Check if meter_id already exists
    registered_meter_ids = {account.meter_id for account in meters}

    if electricity_account.meter_id in registered_meter_ids:
        return False, "Meter ID already registered"

    # Add new account and save all accounts
    meters.append(electricity_account)

    # Convert all accounts to dictionaries for JSON serialization
    accounts_dict = [account.to_dict() for account in meters]

    with open(file_path, 'w') as f:
        json.dump(accounts_dict, f, indent=4)
    return True, "Meter registered successfully"

# Validate meter ID format (XXX-XXX-XXX, digits only)
def is_valid_meter_id(meter_id):
    return bool(re.fullmatch(r"\d{3}-\d{3}-\d{3}", meter_id))

# Global list of meters
meters = load_electricity_accounts_from_file()
meter_readings = {}

# --- FRONTEND MAIN PAGE ---
@app.route("/", methods=["GET"])
def main():
    return render_template("function.html")
# --- BACKEND ROUTES ---
# API 1: Register
# expect input:
# meter id
# region
# area
# dwelling type
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    meter_id = data.get("meter_id")

    if not meter_id:
        return jsonify({"message": "Please provide a meter Id, in the format XXX-XXX-XXX (digits only)"}), HTTPStatus.BAD_REQUEST

    if not is_valid_meter_id(meter_id):
        return jsonify({"message": "Invalid format. Use format XXX-XXX-XXX (digits only)."}), HTTPStatus.BAD_REQUEST

    # Check if meter alreaday exists
    existing_meter = next((meter for meter in meters if meter.meter_id == meter_id), None)
    if existing_meter:
        return jsonify({
            "meter_id": meter_id,
            "message": "This meter is already registered."
        }), HTTPStatus.CONFLICT

    # Check for missing fields: area, region, or dwelling type
    area = data.get("area")
    region = data.get("region")
    dwelling_type = data.get("dwelling_type")

    if not area or not region or not dwelling_type:
        return jsonify({"message": "Please provide a meter Id, area, region, and dwelling type."}), HTTPStatus.BAD_REQUEST

    # Create and save new account
    new_account = ElectricityAccount(
        meter_id=meter_id,
        area=area,
        region=region,
        dwelling_type=dwelling_type
    )

    success, message = save_electricity_accounts_to_file(new_account)

    if not success:
        return jsonify({"message": message}), HTTPStatus.BAD_REQUEST

    return jsonify({
        "meter_id": meter_id,
        "message": "Meter Registered Successfully!"
    }), HTTPStatus.CREATED

# API 2: Get meter reading data from IoT meters
@app.route('/meter-reading', methods=['POST'])
async def meter_reading():
    try:
        # Get form data
        meter_id = request.form.get('meter_id')
        date = request.form.get('date')
        time = request.form.get('time')
        electricity_reading = request.form.get('electricity_reading')

        # Check if meter exists
        existing_meter = next((meter for meter in meters if meter.meter_id == meter_id), None)
        if existing_meter is None:
            return {"error": "Meter does not exist! Please register first."}, HTTPStatus.FORBIDDEN

        try:
            reading = MeterReading.validate_and_create(
                meter_id=meter_id,
                date=date,
                time=time,
                electricity_reading=electricity_reading
            )
        except ValueError as e:
            return {"error": str(e)}, HTTPStatus.BAD_REQUEST

        # Save to CSV if all validations pass
        await save_to_half_hourly_csv([reading.meter_id, reading.date, reading.time, reading.electricity_reading])

        # in-memory dict of MeterReading objects
        if reading.meter_id in meter_readings:
            meter_readings[reading.meter_id].append(reading)
        else:
            meter_readings[reading.meter_id] = [reading]

        # Return success response with the reading data
        return {
            "message": "Reading saved successfully",
            "data": reading.to_dict()
        }, HTTPStatus.ACCEPTED

    except Exception as e:
        return {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
# API 3:Get last reading of today
@app.route('/meter/daily/<meter_id>', methods=['GET'])
def get_daily_meter_usage(meter_id):
    if meter_id not in meters:
        return jsonify({"message": f"Meter {meter_id} not found"}), 404

    try:
        with open('archived_data/daily_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)  
            last_reading = None

            for row in reader:
                if row[0] == meter_id:
                    last_reading = row

            if last_reading:
                return jsonify({
                    "meter_id": last_reading[0],
                    "region":last_reading[1],
                    "area": last_reading[2],
                    "date": last_reading[3],
                    "time": last_reading[4],
                    "usage": last_reading[5]
                }), 200
            return jsonify({"message": f"No readings found for meter {meter_id}"}), 404

    except FileNotFoundError:
        return jsonify({"message": "Daily usage file not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), 500

# API 4: stop server for maintenance and archive for daily,monthly, batch jobs
@app.route("/stop_server", methods=["POST"])
def stop_server():
    global acceptAPI

    acceptAPI = False
    calculate_daily_usage(meters, meter_readings)
    calculate_monthly_usage(meters, meter_readings)
    acceptAPI = True

    return jsonify({"message": "Server is under maintenance."}), 200


# This randomly generates meter readings - WE DO NOT WANT THIS ANYMORE
# @app.route('/generate_readings/<meter_id>', methods=['GET'])
# def generate_readings(meter_id):
#     if meter_id not in meters:
#         return jsonify({"message": "Meter not found, please register first"}), 404

#     timestamps = pd.date_range(start=pd.Timestamp.now().date(), periods=48, freq="30min")
#     meter_readings = [round(random.uniform(0.1, 2.5), 2) for _ in range(len(timestamps))]
#     print(meter_readings)

#     readings = [{"timestamp": str(ts), "reading": reading} for ts, reading in zip(timestamps, meter_readings)]
#     return jsonify({"message": "Readings generated", "meter_id": meter_id, "readings": readings}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)