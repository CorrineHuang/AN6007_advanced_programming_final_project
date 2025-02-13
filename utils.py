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
        daily_usage_data.append([meter_id, account.region, account.area, readings[0].date, daily_usage])

    daily_exists = os.path.exists(daily_file)
    if not daily_exists:
        with open(daily_file, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(["Meter_id", "Region", "Area", "Date", "Daily_Usage (kWh)"])

    try:
        with open(daily_file, 'a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(daily_usage_data)
            print(f"Successfully appended: {daily_usage_data}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def calculate_monthly_usage():
    """Calculate monthly electricity usage and save to CSV."""
    df = pd.read_csv(daily_file)
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime("%b-%Y")
    current_month = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%b-%Y")

    if os.path.exists(monthly_file):
        monthly_df = pd.read_csv(monthly_file)
    else:
        monthly_df = pd.DataFrame(columns = ["Meter_id", "Region", "Area", "Month", "Monthly_Usage (kWh)"])

    monthly_df["Month"] = monthly_df["Month"].astype(str)

    df_month = df[df["Date"] == current_month]
    if df_month.empty:
        print(f"No data found for {current_month}.")
        return

    for meter_id in df_month.Meter_id.unique():
        df_month_id = df_month[df_month["Meter_id"] == meter_id]
        monthly_usage = df_month["Daily_Usage (kWh)"].sum()
        
        # Check if this meter_id already has an entry for the current month
        existing_idx = monthly_df[(monthly_df["Meter_id"] == meter_id) & (monthly_df["Month"] == current_month)].index

        if not existing_idx.empty:
            # Update existing record
            monthly_df.loc[existing_idx, "Monthly_Usage (kWh)"] = monthly_usage
        else:
            # Append new record
            monthly_df = pd.concat([monthly_df, pd.DataFrame([{
                "Meter_id": meter_id,
                "Region": df_month_id.iloc[0]["Region"],
                "Area": df_month_id.iloc[0]["Area"],
                "Month": current_month,
                "Monthly_Usage (kWh)": monthly_usage
            }])], ignore_index = True)

    # Save updated monthly usage data
    monthly_df.to_csv(monthly_file, index = False)
    print("Monthly usage data updated successfully.")