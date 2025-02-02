"""Flask App for Electricity Meter Routes and APIs

During development, APIs and routes can be defined here (check with Mr. Koh on final requirements).
Call generate_meter_readings to get a dict of {meterId: List[MeterReading]}. For testing, the id is typicaly '999' which is baked into the buttons that trigger the APIs on the home page, you may change the id when calling generate_meter_readings. 
"""
import sys
import os
from flask import Flask, jsonify
from meter_readings_generation import generate_meter_readings, MeterReading
from utils import pretty_jsonify
import pandas as pd
import uuid 

sys.path.append(os.getcwd())


# Define API
app = Flask("__name__")


# 1. main page
# Add buttons here if you want to test a new API or route
# Change the location.href to change the endpoint
@app.route("/", methods = ["GET", "POST"])
def main():
    jsonify({"message": "THIS API IS WORKING!"}), 200
    return '''
        <html>
            <body>
                <h1>THIS API IS WORKING!</h1>
                <p>These buttons call APIs for Meter Id 999 (testing purposes).</p>
                <div style="display: flex; flex-direction: column; gap: 10px; width: 500px">
                <button onclick="location.href='/meter/999'" type="button">get_meter method: /meter/999</button>
                <button onclick="location.href='/meter/monthly/999'" type="button">get_monthly_meter_readings: /meter/monthly/999</button>
                </div>
            </body>
        </html>
    '''


meters = {}
@app.route('/register', methods=['POST'])
def register_meter():
    meter_id = str(uuid.uuid4()).replace("-", "")[:11]  # The format is ：999-999-999
    meter_id = f"{meter_id[:3]}-{meter_id[3:6]}-{meter_id[6:9]}"
    
    meters[meter_id] = {
        "readings": [], 
        "registration_time": pd.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("meter_logs.txt", "a") as log_file:
        log_file.write(f"Registered meter: {meter_id} at {meters[meter_id]['registration_time']}\n")
    
    return jsonify({"meter_id": meter_id}), 201


# 2. Get all meter readings by meter ID
@app.route('/meter/<id>', methods=['GET'])
def get_meter(id):
    meter_readings = generate_meter_readings(id) # keys = ['999']
    if meter_readings:
        return pretty_jsonify([meter.__dict__ for meter in meter_readings[id]]), 200
    return pretty_jsonify({"error": f"Meter {id} not found"}), 404


# Get monthly average by meter ID
@app.route('/meter/monthly/<id>', methods=['GET'])
def get_monthly_meter_readings(id):
    meter_readings = generate_meter_readings(id) # keys = ['999']
    if meter_readings:
        df = MeterReading.to_dataframe(meter_readings[id])
        # Should this be its own helper method? If its reusable in future, yes
        monthly_avg = df.groupby(df['date'].dt.strftime('%Y-%m'))['meter_reading'].mean().round(2)
        print(df.head())
        return pretty_jsonify({'meter_reading': id, 'monthly_average': monthly_avg.to_dict() }), 200
    return pretty_jsonify({"error": f"Meter {id} not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)