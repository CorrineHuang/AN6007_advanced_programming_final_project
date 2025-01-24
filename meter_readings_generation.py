import pandas as pd
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# Define the Meter class
class Meter():
    def __init__(self, ID, date, time, meter_reading):
        self.ID = ID
        self.date = date
        self.time= time
        self.meter_reading = meter_reading

    def __repr__(self):
        return (
            f"ID: {self.ID}\n"
            f"Date: {self.date}\n"
            f"Time: {self.time}\n"
            f"Meter_Reading: {self.meter_reading}\n\n"
        )


# Generate half-hourly electricity meter readings
def generate_meter_readings(meter_id, start_date=datetime.now(ZoneInfo("Asia/Singapore"))- timedelta(days=30), end_date=datetime.now(ZoneInfo("Asia/Singapore"))):
    timestamps = pd.date_range(start = start_date, end = end_date, freq = '30min')  # Generate half-hourly timestamps
    
    # Generate cumulative meter readings
    meter_readings = [random.randrange(1000, 5000)]  # Start with the initial reading

    for _ in range(len(timestamps) - 1):
        increment = round(random.uniform(0.1, 2.5), 2)  # Assume half-hourly consumption ranges between 0.1 kWh and 2.5 kWh
        meter_readings.append(meter_readings[-1] + increment)
    
    # Create a list of Meter objects (OOP)
    data = [
        Meter(meter_id, str(timestamp.date()), str(timestamp.time()), str(round(meter_reading,2)))
        for timestamp, meter_reading in zip(timestamps, meter_readings)
    ]
    

    return {meter_id : data}


if __name__ == "__main__":
    meter_id = "SG-METER-001"
    start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Singapore"))
    end_date = datetime.now(ZoneInfo("Asia/Singapore"))

    meter_readings = generate_meter_readings(meter_id, start_date, end_date)
    print(meter_readings)
