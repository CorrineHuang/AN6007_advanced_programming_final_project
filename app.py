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
from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'AN6007 ADVANCED PROGRAMMING - Electricity Meter Service API'
}
swagger = Swagger(app)

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

# --- BACKEND ---
@app.route('/register', methods=['POST'])
def register():
    """
    Register a new meter.
    ---
    tags:
      - Meter Management
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload for registering a meter.
        required: true
        schema:
          type: object
          required:
            - meter_id
            - area
            - region
            - dwelling_type
          properties:
            meter_id:
              type: string
              description: Meter ID in the format XXX-XXX-XXX (numbers only).
            area:
              type: string
              description: The area where the meter is located (e.g. "Jurong").
            region:
              type: string
              description: The region where the meter is located (e.g. "West").
            dwelling_type:
              type: string
              description: Type of dwelling (e.g., "apartment", "house").
    responses:
      201:
        description: Meter registered successfully!
      400:
        description: Bad Request. Some fields are missing or invalid. Several messages are possible in this case.
      409:
        description: Conflict. This meter is already registered.
    """
    data = request.get_json()
    meter_id = data.get("meter_id")

    if not meter_id:
        return jsonify({"message": "Please provide a meter Id, in the format XXX-XXX-XXX (digits only)"}), HTTPStatus.BAD_REQUEST

    if not is_valid_meter_id(meter_id):
        return jsonify({"message": "Invalid format. Use format XXX-XXX-XXX (digits only)."}), HTTPStatus.BAD_REQUEST

    # Check if meter already exists
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

    # Ensure the daily_usage.csv file exists with the appropriate header.
    daily_usage_path = os.path.join(os.getcwd(), 'archived_data', 'daily_usage.csv')
    if not os.path.exists(daily_usage_path):
        with open(daily_usage_path, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write header as expected by get_daily_meter_usage.
            writer.writerow(["meter_id", "region", "area", "date", "time", "usage"])

    return jsonify({
        "meter_id": meter_id,
        "message": "Meter registered successfully!"
    }), HTTPStatus.CREATED

# API 2: Get meter reading data from IoT meters
@app.route('/meter-reading', methods=['POST'])
async def meter_reading():
    """
    Post electricity reading of a single meter to the server.
    ---
    tags:
      - Meter Readings
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: meter_id
        in: formData
        type: string
        required: true
        description: Meter ID in the format XXX-XXX-XXX (numbers only).
      - name: date
        in: formData
        type: string
        required: true
        description: Date of the reading in DD-MM-YYYY format (e.g., 28-01-2020).
      - name: time
        in: formData
        type: string
        required: true
        description: Time of the reading in HH:MM:SS format (e.g., 14:30:11).
      - name: electricity_reading
        in: formData
        type: string
        required: true
        description: The electricity reading value in kWh.
    responses:
      202:
        description: Reading saved successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Reading saved successfully
                data:
                  type: object
                  description: Contains the meter reading details.
      400:
        description: Bad Request due to invalid input values. 
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid reading: [error details]"
      403:
        description: Meter does not exist.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Meter does not exist!"
      500:
        description: Internal Server Error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unexpected error occurred."
    """
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
    """
    Fetch the daily electricity usage for a specified meter.
    @Weiqiang: Logically it is yesterday, cuz the function is to get the latest record of this id, and this data will only appear when we run the stop sever (assumed to be tmr 0 am -1am)
    ---
    tags:
      - Meter Readings
    parameters:
      - name: meter_id
        in: path
        description: Meter ID in the format XXX-XXX-XXX.
        required: true
        type: string
    responses:
      200:
        description: Daily meter reading found.
        schema:
          type: object
          properties:
            meter_id:
              type: string
              example: "123-456-789"
            region:
              type: string
              example: "SomeRegion"
            area:
              type: string
              example: "SomeArea"
            date:
              type: string
              example: "28-01-2020"
            time:
              type: string
              example: "14:30:00"
            usage:
              type: string
              example: "15.2"
      404:
        description: |
          Returned in the following cases:
          - Meter does not exist: "Meter {meter_id} not found"
          - No readings found for the meter: "No readings found for meter {meter_id}"
          - Daily usage file is missing: "Daily usage file not found"
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Meter 123-456-789 not found"
      500:
        description: Internal server error.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Error reading file: [error details]"
    """
    # Verify that the meter exists in our collection.
    existing_meter = next((meter for meter in meters if meter.meter_id == meter_id), None)
    if existing_meter is None:
        return jsonify({"message": f"Meter {meter_id} not found"}), HTTPStatus.NOT_FOUND

    try:
        with open('archived_data/daily_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            # Read header row
            header = next(reader)
            last_reading = None

            for row in reader:
                # Skip any empty rows or rows with insufficient data
                if not row or len(row) < 6:
                    continue
                if row[0] == meter_id:
                    last_reading = row

            if last_reading:
                return jsonify({
                    "meter_id": last_reading[0],
                    "region": last_reading[1],
                    "area": last_reading[2],
                    "date": last_reading[3],
                    "time": last_reading[4],
                    "usage": last_reading[5]
                }), HTTPStatus.OK

            return jsonify({"message": f"No readings found for meter {meter_id}"}), HTTPStatus.NOT_FOUND

    except FileNotFoundError:
        return jsonify({"message": "Daily usage file not found"}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR

# API 4: stop server for maintenance and archive for daily,monthly, batch jobs
@app.route("/stop_server", methods=["POST"])
def stop_server():
    """
    Stop the server for maintenance and archive daily, monthly, and batch jobs.
    ---
    tags:
      - Server Maintenance
    responses:
      200:
        description: Server maintenance and archival tasks were completed successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Server is under maintenance."
    """
    global acceptAPI

    acceptAPI = False
    calculate_daily_usage(meters, meter_readings)
    calculate_monthly_usage(meters)
    acceptAPI = True

    return jsonify({"message": "Server is under maintenance."}), HTTPStatus.ACCEPTED


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