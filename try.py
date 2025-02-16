# from datetime import datetime
import os
import re
# import random
import pandas as pd
from flask import Flask, json, request, jsonify,render_template
from http import HTTPStatus
import json
import csv
from models.electricity_account import ElectricityAccount
from models.meter_reading import MeterReading
from utils import save_to_half_hourly_csv, calculate_daily_usage, calculate_monthly_usage
from flask_cors import CORS
file_path = os.path.join(os.getcwd(), 'archived_data', 'electricity_accounts.json')
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

meter_accounts = load_electricity_accounts_from_file()
meter_list = [i.meter_id for i in meter_accounts]
meter_readings = {}

def get_daily_meter_usage(meter_id):
    if meter_id not in meter_list:
        return jsonify({"message": f"Meter {meter_id} not found"}), 404
    try:
        with open('archived_data/daily_usage.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)  
            last_reading = None

            for row in reader:
                if len(row) < 4:
                    continue
                if row[0] == meter_id:
                    last_reading = row

            if last_reading:
                return {
                    "meter_id": last_reading[0],
                    # "region":last_reading[1],
                    # "area": last_reading[2],
                    "date": last_reading[1],
                    "time": last_reading[2],
                    "usage": last_reading[3]
                }, 200
            return  401

    except FileNotFoundError:
        return 404
    except Exception as e:
        return  e,5001

print(get_daily_meter_usage('999-999-993'))
