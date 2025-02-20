import os
import csv
import pandas as pd
from datetime import datetime
import pytz
import json
import re

from models.electricity_account import ElectricityAccount


file_path = os.path.join(os.getcwd(), 'archived_data', 'electricity_accounts.json')
half_hourly_readings_csv_filepath = 'archived_data/half_hourly_readings.csv'
daily_file = "archived_data/daily_usage.csv"
monthly_file = "archived_data/monthly_usage.csv"


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
def save_electricity_accounts_to_file(electricity_account: ElectricityAccount, meter_list, meter_accounts):
    """Save a new meter to the file"""
    # Check if meter_id already exists
    if electricity_account.meter_id in meter_list:
        return False, "Meter ID already registered"

    # Add new account and save all accounts
    meter_accounts.append(electricity_account)

    # Convert all accounts to dictionaries for JSON serialization
    accounts_dict = [account.to_dict() for account in meter_accounts]

    with open(file_path, 'w') as f:
        json.dump(accounts_dict, f, indent=4)
    return True, "Meter registered successfully"


# Validate meter ID format (XXX-XXX-XXX, digits only)
def is_valid_meter_id(meter_id):
    return bool(re.fullmatch(r"\d{3}-\d{3}-\d{3}", meter_id))


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

def calculate_daily_usage(meter_accounts, meter_readings):
    """Calculate daily electricity usage and save to CSV."""
    daily_usage_data = []

    for meter_id, readings in meter_readings.items():
        account = next((meter for meter in meter_accounts if meter.meter_id == meter_id), None)

        daily_usage = readings[-1].electricity_reading - readings[0].electricity_reading
        daily_usage_data.append([meter_id, account.region, account.area, account.dwelling_type, readings[0].date, daily_usage])

    daily_exists = os.path.exists(daily_file)

    try:
        with open(daily_file, 'a', newline='') as file:
            writer = csv.writer(file)
            
            # If file is newly created, write the header
            if not daily_exists:
                writer.writerow(["Meter_id", "Region", "Area", "Dwelling_type", "Date", "Daily_Usage (kWh)"])
            
            for row in daily_usage_data:
                writer.writerow(row)
                print(f"Successfully appended: {row}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def calculate_monthly_usage():
    """Calculate monthly electricity usage and save to CSV."""
    if not os.path.exists(daily_file):
        print(f"Error: {daily_file} does not exist.")
        return

    df = pd.read_csv(daily_file)
    if df.empty:
        print(f"Error: {daily_file} is empty.")
        return

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime("%Y-%b")

    current_month = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%Y-%b")
    # I think we should give users the last month, not the current month 
    if os.path.exists(monthly_file):
        monthly_df = pd.read_csv(monthly_file)
    else:
        monthly_df = pd.DataFrame(columns=["Meter_id", "Region", "Area", "Dwelling_type", "Month", "Monthly_Usage (kWh)"])

    df_month = df[df["Date"] == current_month]

    if df_month.empty:
        print(f"No data found for {current_month}.")
        return

    for meter_id in df_month["Meter_id"].unique():
        df_month_id = df_month[df_month["Meter_id"] == meter_id]
        monthly_usage = df_month_id["Daily_Usage (kWh)"].sum()
        
        # Check if this meter_id already has an entry for the current month
        existing_idx = monthly_df[(monthly_df["Meter_id"] == meter_id) & (monthly_df["Month"] == current_month)].index

        if not existing_idx.empty:
            monthly_df.loc[existing_idx, "Monthly_Usage (kWh)"] = monthly_usage
            print(f"Updated usage for Meter ID {meter_id}.")
        else:
            new_record = {
                "Meter_id": meter_id,
                "Region": df_month_id.iloc[0]["Region"],
                "Area": df_month_id.iloc[0]["Area"],
                "Dwelling_type": df_month_id.iloc[0]["Dwelling_type"],
                "Month": current_month,
                "Monthly_Usage (kWh)": monthly_usage
            }
            monthly_df = pd.concat([monthly_df, pd.DataFrame([new_record])], ignore_index=True)
            print(f"Added new record for Meter ID {meter_id}.")

    # Save updated monthly usage data
    monthly_df.to_csv(monthly_file, index=False)
    print(f"Monthly usage data saved successfully to {monthly_file}.")