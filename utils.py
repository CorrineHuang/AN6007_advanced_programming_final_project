import os
import csv

half_hourly_readings_csv_filepath = 'archived_data\half_hourly_readings.csv'

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