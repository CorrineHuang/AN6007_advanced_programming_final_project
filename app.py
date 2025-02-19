import os
from flask import Flask, request, jsonify,render_template
from http import HTTPStatus
import csv
import time
from models.electricity_account import ElectricityAccount
from models.meter_reading import MeterReading
from utils import is_valid_meter_id, load_electricity_accounts_from_file, save_electricity_accounts_to_file, save_to_half_hourly_csv, calculate_daily_usage, calculate_monthly_usage
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'AN6007 ADVANCED PROGRAMMING - Electricity Meter Service API'
}
swagger = Swagger(app)
CORS(app)

# Globals for in-memory storage
meter_accounts = load_electricity_accounts_from_file()
meter_list = [i.meter_id for i in meter_accounts] # known meter Ids
meter_readings = {}

# Global for server online status
acceptAPI = True


#####################
# Frontend Route
#####################
@app.route("/", methods=["GET"])
def main():
    return render_template("function.html")


#####################
# Backend Internal API
#####################
# API 1: Register
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
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE
    
    data = request.get_json()
    meter_id = data.get("meter_id")

    if not meter_id:
        return jsonify({"message": "Please provide a meter Id, in the format XXX-XXX-XXX (digits only)"}), HTTPStatus.BAD_REQUEST

    if not is_valid_meter_id(meter_id):
        return jsonify({"message": "Invalid format. Use format XXX-XXX-XXX (digits only)."}), HTTPStatus.BAD_REQUEST

    # Check if meter already exists
    if meter_id in meter_list:
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

    success, message = save_electricity_accounts_to_file(new_account, meter_list=meter_list, meter_accounts=meter_accounts)
    if not success:
        return jsonify({"message": message}), HTTPStatus.BAD_REQUEST
    
    meter_list.append(meter_id)

    # # Ensure the daily_usage.csv file exists with the appropriate header.
    # daily_usage_path = os.path.join(os.getcwd(), 'archived_data', 'daily_usage.csv')
    # if not os.path.exists(daily_usage_path):
    #     with open(daily_usage_path, 'w', newline='') as file:
    #         writer = csv.writer(file)
    #         # Write header as expected by get_daily_meter_usage.
    #         writer.writerow(["meter_id", "region", "area", "date", "time", "usage"])

    return jsonify({
        "meter_id": meter_id,
        "message": "Meter registered successfully!"
    }), HTTPStatus.CREATED


# API 2: Get meter reading data from IoT meters
@app.route('/meter-readings', methods=['POST'])
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
        description: Meter ID in the format 123-456-789 (digits only).
      - name: date
        in: formData
        type: string
        required: true
        description: Date of the reading in YYYY-MM-DD format (e.g., 2020-01-28).
      - name: time
        in: formData
        type: string
        required: true
        description: Time of the reading in HH:MM format (e.g., 14:30).
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
                  example: "Reading saved successfully"
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
                  example: "Meter does not exist! Please register first."
      503:
        description: Service Unavailable. The server is temporarily offline for maintenance.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "The server is temporarily offline for maintenance."
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
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE

    try:
        # Get form data
        meter_id = request.form.get('meter_id')
        date = request.form.get('date')
        time = request.form.get('time')
        electricity_reading = request.form.get('electricity_reading')

        # Check if meter exists
        if meter_id not in meter_list:
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

      
# API 3: Get last daily reading for a specific meter Id
@app.route('/meters/<meter_id>/daily/latest', methods=['GET'])
def get_latest_daily_meter_usage(meter_id):
    """
    Get the latest daily meter usage reading.
    ---
    tags:
      - Meter Readings
    parameters:
      - name: meter_id
        in: path
        type: string
        required: true
        description: Meter ID in the format 123-456-789 (digits only).
    responses:
      200:
        description: The latest daily meter usage reading.
        schema:
          type: object
          properties:
            meter_id:
              type: string
              example: "123-456-789"
            region:
              type: string
              example: "West"
            area:
              type: string
              example: "Jurong"
            date:
              type: string
              example: "2020-01-28"
            usage:
              type: string
              example: "150"
      404:
        description: No readings found for the meter or file not found.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "No readings found for meter 123-456-789"
      503:
        description: Service Unavailable. The server is temporarily offline for maintenance.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "The server is temporarily offline for maintenance."
      500:
        description: Internal Server Error.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Error reading file: [error details]"
    """
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE

    try:
        with open('archived_data/daily_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            # Read header row
            header = next(reader)
            last_reading = None
            for row in reader:
                # Skip any empty rows
                if not row:
                    continue
                if row[0] == meter_id:
                    last_reading = row

            if last_reading:
                return jsonify({
                    "meter_id": last_reading[0],
                    "region": last_reading[1],
                    "area": last_reading[2],
                    "dwelling_type": last_reading[3],
                    "date": last_reading[4],
                    "usage": last_reading[5]
                }), 200
            return jsonify({"message": f"No readings found for meter {meter_id}"}), 404

    except FileNotFoundError:
        return jsonify({"message": "Daily usage file not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR
  
      
# API 4: Get last monthly reading for a specific meter Id  
@app.route('/meters/<meter_id>/monthly/latest', methods=['GET'])
def get_latest_monthly_meter_usage(meter_id):
    """
    Get the latest monthly meter usage reading.
    ---
    tags:
      - Meter Readings
    parameters:
      - name: meter_id
        in: path
        type: string
        required: true
        description: Meter ID in the format 123-456-789 (digits only).
    responses:
      200:
        description: The latest monthly meter usage reading.
        schema:
          type: object
          properties:
            meter_id:
              type: string
              example: "123-456-789"
            region:
              type: string
              example: "West"
            area:
              type: string
              example: "Jurong"
            date:
              type: string
              example: "2020-01-28"
            usage:
              type: string
              example: "150"
      404:
        description: No readings found for the meter or file not found.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "No readings found for meter 123-456-789"
      503:
        description: Service Unavailable. The server is temporarily offline for maintenance.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "The server is temporarily offline for maintenance."
      500:
        description: Internal Server Error.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Error reading file: [error details]"
    """
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE

    try:
        with open('archived_data/monthly_usage.csv', 'r', newline='') as file:
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
                    "dwelling_type": last_reading[3],
                    "date": last_reading[4],
                    "usage": last_reading[5]
                }), 200
            return jsonify({"message": f"No readings found for meter {meter_id}"}), 404

    except FileNotFoundError:
        return jsonify({"message": "Monthly usage file not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), 500


# API 5: Stop the server and perform batch jobs for maintenance
@app.route("/stop_server", methods=["POST"])
def stop_server():
    """
    Stop the server for maintenance, clear memory and archive daily, monthly, and batch jobs.
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
              example: "Server is shutting down. We are working on batch jobs. Good Night!"
    """
    global acceptAPI

    acceptAPI = False
    calculate_daily_usage(meter_accounts, meter_readings)
    calculate_monthly_usage()
    # time.sleep(5)
    meter_readings.clear()
    acceptAPI = True

    return jsonify({"message": "Server is shutting down. We are working on batch jobs. Good Night!"}), 200


#####################
# External APIs to Monetize
#####################
# External API 1: Get all daily readings for all meters
@app.route('/meters/daily', methods=['GET'])
def get_daily_readings():
    """
    Get daily usage readings for all meters.
    ---
    tags:
      - Meter Readings
    responses:
      200:
        description: Daily readings retrieved successfully.
        schema:
          type: object
          properties:
            readings:
              type: array
              items:
                type: object
                properties:
                  region:
                    type: string
                    example: "West"
                  area:
                    type: string
                    example: "Jurong"
                  date:
                    type: string
                    example: "2020-01-28"
                  usage:
                    type: string
                    example: "150"
      404:
        description: No readings found or the daily usage file is not available.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "No readings found."
      503:
        description: Service unavailable. The server is temporarily offline for maintenance.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "The server is temporarily offline for maintenance."
      500:
        description: Internal server error.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Error reading file: [error details]"
    """
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE
    
    try:
        with open('archived_data/daily_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            readings = []

            for row in reader:
                readings.append({
                    "region":row[1],
                    "area": row[2],
                    "dwelling_type": row[3],
                    "date": row[4],
                    "usage": row[5]
                }), 200

            if readings:
                return jsonify({
                    "readings": readings
                }), 200
            return jsonify({"message": f"No readings found."}), 404

    except FileNotFoundError:
        return jsonify({"message": "Daily usage file not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), 500

    
# External API 2: Get all monthly readings for all meters
@app.route('/meters/monthly', methods=['GET'])
def get_monthly_readings():
    """
    Get monthly usage readings for all meters.
    ---
    tags:
      - Meter Readings
    responses:
      200:
        description: Monthly readings retrieved successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                readings:
                  type: array
                  items:
                    type: object
                    properties:
                      region:
                        type: string
                        example: "West"
                      area:
                        type: string
                        example: "Jurong"
                      date:
                        type: string
                        example: "2020-01-28"
                      usage:
                        type: number
                        example: 150.0
      404:
        description: No readings found or the monthly usage file is not available.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "No readings found."
      503:
        description: Service unavailable. The server is temporarily offline for maintenance.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "The server is temporarily offline for maintenance."
      500:
        description: Internal server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Error reading file: [error details]"
    """
    if not acceptAPI:
        return jsonify({"message": f"The server is temporarily offline for maintenance."}), HTTPStatus.SERVICE_UNAVAILABLE
    
    try:
        with open('archived_data/monthly_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            readings = []

            for row in reader:
                    readings.append({
                      "region": row[1],
                      "area": row[2],
                      "dwelling_type": row[3],
                      "date": row[4],
                      "usage": float(row[5])
                  })

            if readings:
                return jsonify({
                    "readings": readings
                }), 200
            return jsonify({"message": f"No readings found."}), 404

    except FileNotFoundError:
        return jsonify({"message": "Monthly usage file not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error reading file: {str(e)}"}), 500
      

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)