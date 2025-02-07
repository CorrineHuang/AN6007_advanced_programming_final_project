import os
import csv
import pandas as pd
from datetime import datetime
import pytz


half_hourly_readings_csv_filepath = 'archived_data\half_hourly_readings.csv'
daily_file = "archived_data/daily_usage.csv"
monthly_file = "archived_data/monthly_usage.csv"

async def save_to_half_hourly_csv(data):
    file_exists = os.path.exists(half_hourly_readings_csv_filepath)

    # If file doesn't exist, create it with headers
    if not file_exists:
        with open(half_hourly_readings_csv_filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Meter Id', 'Date', 'Time', 'Electricity Reading (kWh)'])

    # Append the new data
    try:
        with open(half_hourly_readings_csv_filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print(f"Successfully appended: {data}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def calculate_daily_usage(meters, meter_readings):
    """Calculate daily electricity usage and save to CSV."""
    daily_usage_data = []
    for meter_id, readings in meter_readings.items():
        account = next((meter for meter in meters if meter.meter_id == meter_id), None)

        daily_usage = readings[-1].electricity_reading - readings[0].electricity_reading
        daily_usage_data.append([meter_id, readings[0].date, account.region, account.area, daily_usage])

    daily_exists = os.path.exists(daily_file)
    if not daily_exists:
        with open(daily_file, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(["Meter_id", "Region", "Area", "Date", "Time", "Daily_Usage (kWh)"])

    try:
        with open(daily_file, 'a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(daily_usage_data)
            print(f"Successfully appended: {daily_usage_data}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def calculate_monthly_usage(meters, meter_readings):
    """Calculate monthly electricity usage and save to CSV."""
    monthly_usage_data = []

    df = pd.read_csv(daily_file)
    df['Date'] = pd.to_datetime(df['Date']).strftime("%m-%Y")
    current_month = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%m-%Y")

    for meter_id, readings in meter_readings.items():
        monthly_usage = df[]

        
        if df_month.empty:
            return






    

    for meter_id, readings in meter_readings.items():
        account = next((meter for meter in meters if meter.meter_id == meter_id), None)

        monthly_usage = readings[-1].electricity_reading - readings[0].electricity_reading
        monthly_usage_data.append([meter_id, readings[0].date, account.region, account.area, monthly_usage])

    monthly_exists = os.path.exists(monthly_file)
    if not monthly_exists:
        with open(monthly_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Meter_id", "Region", "Area", "Month", "monthly_Usage (kWh)"])

    try:
        with open(monthly_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(monthly_usage_data)
            print(f"Successfully appended: {monthly_usage_data}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise