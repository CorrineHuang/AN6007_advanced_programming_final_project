from datetime import datetime, timedelta
import pandas as pd 
import random
from zoneinfo import ZoneInfo

class ElectricityAccount:
    def __init__(self, meter_id):
        """
        :param meter_id: primary key
        """
        self.meter_id = meter_id
        # the format of meter_id is 999-999-999
        # we need a function to check the format of meter_id "999-999-999"
        self.readings = []  
        # readings of every 30 mins，
        # format：[{"timestamp": "YYYY-MM-DD HH:MM:SS", "reading": 100.5}]
        # we can think about data structure here
        self.registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.billing_history = []
        self.owner = None
        self.status = 'On' # [on, off]
        # billing history，format：[{"month": "YYYY-MM", "usage": 1500.5}]
        # we can think about data structure here.
    # can add a __str__ here. 

    def __str__(self):
        return f'''
    The meter {self.meter_id} is owned by {self.owner}.
    Registration_time is {self.registration_time} and status is {self.status}.
    Readings are {self.readings}.
    Billing history is {self.billing_history} 
     '''

    def add_reading(self, new_reading):
        """
        add new readings
        :param reading: /kWh
        """
        if not isinstance(new_reading, (int, float)) or new_reading < 0:
            raise ValueError("Invalid reading value")
        # we can update here to check format 
    
        self.readings.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reading": new_reading
        })

    def get_peroid_usage(self, period="day"):
        # we need to think here, if we want to user to enter: day,month,last month, 
        # or they just enter 7 for July,8 for August 
        """
        calculate total usage of a period
        :param period: time period(day/week/month/last_month)
        :return: kWh
        """
        # we can add more time period here like 3 months, 6 months and a year.
        # and we need to make sure that users know what period options they can choose.

        now = datetime.now()
        
        if period == "day":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=now.weekday())
        elif period == "month":
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "last_month":
            start_time = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        else:
            raise ValueError("Invalid period")
        
        # Filtering 
        filtered_readings = [
            r["reading"] for r in self.readings
            if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") >= start_time
        ]
        
        if not filtered_readings:
            return 0 
        
        first_reading = filtered_readings[0]
        last_reading = filtered_readings[-1]
        
        difference = last_reading - first_reading
        
        return difference

    def generate_billing(self):
        """
        generate bill for the current month or last month 
        """
        current_month = datetime.now().strftime("%Y-%m")
        monthly_usage = self.get_peroid_usage(period="month")

        # append the the billing history
        self.billing_history.append({
            "month": current_month,
            "usage": monthly_usage
        })

    def archive_daily_readings(self):
        """
        archive for today
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with open(f"readings_{self.meter_id}_{today}.txt", "w") as file:
            for reading in self.readings:
                file.write(f"{reading['timestamp']}, {reading['reading']} kWh\n")

    def archive_monthly_billing(self):
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        with open(f"billing_{self.meter_id}_{last_month}.txt", "w") as file:
            for bill in self.billing_history:
                if bill["month"] == last_month:
                    file.write(f"{bill['month']}, {bill['usage']} kWh\n")

    def generate_meter_readings(self, interval="30min", start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.now(ZoneInfo("Asia/Singapore")).date() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now(ZoneInfo("Asia/Singapore")).date()

        timestamps = pd.date_range(start=start_date, end=end_date, freq=interval)

        meter_readings = [random.randrange(1000, 5000)]

        for _ in range(len(timestamps) - 1):
            increment = round(random.uniform(0.1, 2.5), 2)  
            meter_readings.append(meter_readings[-1] + increment)

        for timestamp, reading in zip(timestamps, meter_readings):
            self.readings.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "reading": reading
            })
if __name__ == "__main__":
    test_account = ElectricityAccount('123-456-789')
    test_account.owner = 'Tom'

    # test_account.add_reading(30)
    print(test_account)

    test_account.generate_meter_readings(interval="30min")
    # test_account.generate_meter_readings(interval="10s")

    print("Generated readings (30min interval):")
    for reading in test_account.readings[:5]:
        print(reading)

    daily_usage = test_account.get_peroid_usage(period="day")
    print(f"\nDaily usage: {daily_usage} kWh")

    test_account.generate_billing()
    print(f"\nBilling history: {test_account.billing_history}")

    test_account.archive_daily_readings()
    test_account.archive_monthly_billing()
    print(test_account)