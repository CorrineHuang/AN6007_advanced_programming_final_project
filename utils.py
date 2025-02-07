import os
import csv

daily_csv_filepath = 'archived_data\daily.csv'

async def save_to_daily_csv(data):
    file_exists = os.path.exists(daily_csv_filepath)

    # If file doesn't exist, create it with headers
    if not file_exists:
        with open(daily_csv_filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Meter Id', 'Date', 'Time', 'Electricity Reading (kWh)'])

    # Append the new data
    try:
        with open(daily_csv_filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print(f"Successfully appended: {data}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise