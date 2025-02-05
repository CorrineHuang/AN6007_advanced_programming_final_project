import pandas as pd
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# Define the MeterReading class
class MeterReading():
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
    
    def to_dict(self):
        return {
            'ID': self.ID,
            'date': self.date,
            'time': self.time,
            'meter_reading': self.meter_reading
        }
    
    @staticmethod
    def to_dataframe(meter_readings_list):
        """Convert a list of MeterReading objects to a DataFrame"""
        df = pd.DataFrame([mr.to_dict() for mr in meter_readings_list])
        df['date'] = pd.to_datetime(df['date'])
        df['meter_reading'] = df['meter_reading'].astype(float)
        return df


# Generate half-hourly electricity meter readings
# Must review again as the purpose of this function is unclear due to lack of actual test data - will it generate data for one meter or for all? Will this change once Mr Koh gives us actual data
def generate_meter_readings(meter_id, start_date=datetime.now(ZoneInfo("Asia/Singapore")).date() - timedelta(days=30), end_date=datetime.now(ZoneInfo("Asia/Singapore")).date()):
    """
    Generate a series of meter readings taken every 30 minutes for a given meter ID between the specified start and end dates.

    Args:
        meter_id (str): The unique identifier for the meter.
        start_date (datetime, optional): The start date for generating readings. 
            Defaults to 30 days before the current date.
        end_date (datetime, optional): The end date for generating readings. 
            Defaults to the current date.

    Returns:
        dict: {meter_id: MeterReading} A dictionary with the meter_id as the key and a list of MeterReading objects as the value. Each MeterReading object contains the meter ID, date, 
        time, and the formatted meter reading.
    """
    timestamps = pd.date_range(start = start_date, end = end_date, freq = '30min')  # Generate half-hourly timestamps
    
    # Generate cumulative meter readings
    meter_readings = [random.randrange(1000, 5000)]  # Start with the initial reading

    for _ in range(len(timestamps) - 1):
        increment = round(random.uniform(0.1, 2.5), 2)  # Assume half-hourly consumption ranges between 0.1 kWh and 2.5 kWh
        meter_readings.append(meter_readings[-1] + increment)
    
    # Create a list of Meter objects (OOP)
    data = [
        MeterReading(meter_id, str(timestamp.date()), str(timestamp.time()), f"{round(meter_reading,2):.2f}")
        for timestamp, meter_reading in zip(timestamps, meter_readings)
    ]

    return {meter_id : data}


if __name__ == "__main__":
    meter_id = "SG-METER-001"
    start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Singapore"))
    end_date = datetime.now(ZoneInfo("Asia/Singapore"))

    meter_readings = generate_meter_readings(meter_id, start_date, end_date)
    print(meter_readings)
