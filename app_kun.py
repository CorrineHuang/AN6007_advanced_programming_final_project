import os
import re
import random
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load all current meter accounts from file
def load_meters_from_file(file_name='meters.txt'):
    meters_list = []
    file_path = os.path.join(os.getcwd(), file_name)
    try:
        with open(file_path, "r") as file:
            for line in file:
                meter_id = line.strip()
                if meter_id:
                    meters_list.append(meter_id)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Please check.")
    return meters_list

# Save a new meter to the file
def save_meter_to_file(meter_id, file_name='meters.txt'):
    with open(file_name, "a") as file:
        file.write(meter_id + "\n")

# Validate meter ID format (XXX-XXX-XXX, digits only)
def is_valid_meter_id(meter_id):
    return bool(re.fullmatch(r"\d{3}-\d{3}-\d{3}", meter_id))

# Global list of meters
meters = load_meters_from_file()

# --- FRONTEND MAIN PAGE ---
@app.route("/", methods=["GET"])
def main():
    return '''
        <html>
            <head>
                <title>Electricity Meter Service</title>
                <script>
                    function registerMeter() {
                        var meterId = document.getElementById("meterId").value.trim();

                        if (!meterId) {
                            document.getElementById("result").innerText = "Please enter a Meter ID.";
                            return;
                        }

                        fetch('/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ meter_id: meterId })
                        })
                        .then(response => response.json().then(data => ({ status: response.status, body: data }))) 
                        .then(response => {
                            document.getElementById("result").innerText = response.body.message;
                            document.getElementById("meterId").value = response.body.meter_id;
                        })
                        .catch(error => {
                            document.getElementById("result").innerText = "Error registering meter. Please try again.";
                        });
                    }

                    function generateReadings() {
                        var meterId = document.getElementById("meterId").value;
                        if (!meterId) {
                            document.getElementById("result").innerText = "Please enter a valid Meter ID.";
                            return;
                        }
                        fetch('/generate_readings/' + meterId)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById("result").innerText = "Readings generated for Meter: " + meterId;
                        })
                        .catch(error => {
                            document.getElementById("result").innerText = "Error generating readings.";
                        });
                    }

                    function viewDailyUsage() {
                        var meterId = document.getElementById("meterId").value;
                        if (!meterId) {
                            document.getElementById("result").innerText = "Please enter a valid Meter ID.";
                            return;
                        }
                        window.location.href = "/meter/daily/" + meterId;
                    }

                    function viewMonthlyUsage() {
                        var meterId = document.getElementById("meterId").value;
                        if (!meterId) {
                            document.getElementById("result").innerText = "Please enter a valid Meter ID.";
                            return;
                        }
                        window.location.href = "/meter/monthly/" + meterId;
                    }
                </script>
            </head>
            <body>
                <h1>Electricity Meter Service</h1>
                <label for="meterId">Enter Meter ID (format: XXX-XXX-XXX):</label>
                <input type="text" id="meterId" name="meterId" placeholder="e.g., 123-456-789">
                
                <button onclick="registerMeter()">Register Meter</button>
                <button onclick="generateReadings()">Generate Readings</button>
                <button onclick="viewDailyUsage()">View Daily Usage</button>
                <button onclick="viewMonthlyUsage()">View Monthly Usage</button>

                <p id="result"></p>
            </body>
        </html>
    '''

# --- BACKEND ROUTES ---

@app.route('/register', methods=['POST'])
def register_meter():
    data = request.get_json()
    user_meter_id = data.get("meter_id")

    if not user_meter_id:
        return jsonify({"message": "Please enter a Meter ID"}), 400
    if not is_valid_meter_id(user_meter_id):
        return jsonify({"message": "Invalid format. Use format XXX-XXX-XXX (digits only)."}), 400

    if user_meter_id in meters:
        return jsonify({
            "meter_id": user_meter_id,
            "message": "The Meter is already registered. You can view your data."
        }), 200

    # Register new meter
    meters.append(user_meter_id)
    save_meter_to_file(user_meter_id)
    
    return jsonify({"meter_id": user_meter_id, "message": "Meter Registered Successfully!"}), 201

@app.route('/generate_readings/<meter_id>', methods=['GET'])
def generate_readings(meter_id):
    if meter_id not in meters:
        return jsonify({"message": "Meter not found, please register first"}), 404

    timestamps = pd.date_range(start=pd.Timestamp.now().date(), periods=48, freq="30min")
    meter_readings = [round(random.uniform(0.1, 2.5), 2) for _ in range(len(timestamps))]
    print(meter_readings)

    readings = [{"timestamp": str(ts), "reading": reading} for ts, reading in zip(timestamps, meter_readings)]
    return jsonify({"message": "Readings generated", "meter_id": meter_id, "readings": readings}), 200


@app.route('/meter/daily/<meter_id>', methods=['GET'])
def get_daily_meter_readings(meter_id):
    if meter_id not in meters:
        return jsonify({"message": f"Meter {meter_id} not found"}), 404

    daily_usage = round(random.uniform(10, 50), 2)  
    # Simulating monthly usage, we need to change 
    return jsonify({'meter_id': meter_id, 'daily_usage': daily_usage}), 200


@app.route('/meter/monthly/<meter_id>', methods=['GET'])
def get_monthly_meter_readings(meter_id):
    if meter_id not in meters:
        return jsonify({"message": f"Meter {meter_id} not found"}), 404

    monthly_usage = round(random.uniform(300, 1500), 2)  
    # Simulating monthly usage, we need to change 
    return jsonify({'meter_id': meter_id, 'monthly_usage': monthly_usage}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)