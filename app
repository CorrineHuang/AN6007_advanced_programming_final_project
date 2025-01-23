#Imports
from flask import Flask, jsonify, request
import pandas as pd
import random
from datetime import datetime

# OOP create class

class Meter():
    def __init__(self, ID, date, time, meter_reading):
        self.ID = ID
        self.date = date
        self.time= time
        self.meter_reading = meter_reading
        
    
    def __repr__(self):
        return (
            f"  ID: {self.ID}\n"
            f"  Date: {self.date}\n"
            f"  Time: {self.time}\n"
            f"  Meter_Reading: {self.meter_reading}\n\n"
        )

# Fake electricity generation
def generate_fake_meter_readings(meter_id, start_date, end_date):
    """
    Generate fake half-hourly cumulative electricity meter readings.
    
    Parameters:
        meter_id (str): Unique identifier for the meter.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
        pd.DataFrame: DataFrame containing fake cumulative meter readings.
    """
    # Generate half-hourly timestamps
    timestamps = pd.date_range(start=start_date, end=end_date, freq='30T')
    
    # Generate random consumption increments (kWh) for each half-hour
    # Assuming typical half-hourly consumption ranges between 0.1 kWh and 2.5 kWh
    consumption_increments = [round(random.uniform(0.1, 2.5), 2) for _ in range(len(timestamps))]
    
    # Calculate cumulative meter readings
    meter_readings = [random.random()]  # Start with the initial reading
    for increment in consumption_increments:
        meter_readings.append(meter_readings[-1] + increment)
    
    # Remove the first value (initial reading) to align with timestamps
    meter_readings = meter_readings[1:]
    
    # Create a DataFrame
    data = {
        "Meter ID": [meter_id] * len(timestamps),
        "Timestamps": timestamps,
        "Meter Reading (kWh)": meter_readings
    }
    df = pd.DataFrame(data)
    
    return df

# Generate fake data for a specific meter
meter_id = "SG-METER-001"
start_date = "2025-01-01"
end_date = datetime.now()
df = generate_fake_meter_readings(meter_id, start_date, end_date)

# Display the first few rows
print(df)


list = []
for i, row in df.iterrows():
    list.append(Meter(row['Meter ID'], row['Date'], row['Time'], row['Meter Reading (kWh)']))

#Define API

app = Flask(__name__)

