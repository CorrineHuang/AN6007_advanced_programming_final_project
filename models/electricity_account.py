class ElectricityAccount:
    def __init__(self, meter_id, area, region, dwelling_type):
        self.meter_id = meter_id
        self.area = area
        self.region = region
        self.dwelling_type = dwelling_type

    def __str__(self):
        return (
            f"Meter Id: {self.meter_id}\n"
            f"Area: {self.area}\n"
            f"Region: {self.region}\n"
            f"Dwelling Type: {self.dwelling_type}\n"
        )

    def to_dict(self):
        """Convert the ElectricityAccount object to a dictionary"""
        return {
            'meter_id': self.meter_id,
            'area': self.area,
            'region': self.region,
            'dwelling_type': self.dwelling_type
        }

    @classmethod
    def from_dict(cls, data):
        """Create an ElectricityAccount instance from a dictionary"""
        return cls(
            meter_id=data.get('meter_id'),
            area=data.get('area'),
            region=data.get('region'),
            dwelling_type=data.get('dwelling_type')
        )

    # def add_reading(self, new_reading):
    #     """
    #     add new readings
    #     :param reading: /kWh
    #     """
    #     if not isinstance(new_reading, (int, float)) or new_reading < 0:
    #         raise ValueError("Invalid reading value")
    #     # we can update here to check format
    #     self.readings.append({
    #         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #         "reading": new_reading
    #     })

    # SUBTRACTION PART
    # def get_peroid_usage(self, period="day"):
    #     # we need to think here, if we want to user to enter: day,month,last month, 
    #     # or they just enter 7 for July,8 for August 
    #     """
    #     calculate total usage of a period
    #     :param period: time period(day/week/month/last_month)
    #     :return: kWh
    #     """
    #     # we can add more time period here like 3 months, 6 months and a year.
    #     # and we need to make sure that users know what period options they can choose.

    #     now = datetime.now()
    #     if period == "day":
    #         start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #     elif period == "week":
    #         start_time = now - timedelta(days=now.weekday())
    #     elif period == "month":
    #         start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    #     elif period == "last_month":
    #         start_time = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    #     else:
    #         raise ValueError("Invalid period")
        
    #     # Filtering 
    #     filtered_readings = [
    #         r["reading"] for r in self.readings
    #         if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") >= start_time
    #     ]
        
    #     if not filtered_readings:
    #         return 0 
        
    #     first_reading = filtered_readings[0]
    #     last_reading = filtered_readings[-1]
        
    #     difference = last_reading - first_reading
        
    #     return difference
    

    # with open(f"readings_{self.meter_id}_{today}.csv", mode="w", newline="") as file:
    # writer = csv.writer(file)
    
    # # Writing the header row
    # writer.writerow(["timestamp", "reading (kWh)"])
    
    # # Writing the data rows
    # for reading in readings:
    #     writer.writerow([reading["timestamp"], reading["reading"]])

    # def backup_daily_readings(self, readings: List[str]):
    #     """
    #     Archived as timestamp - reading into .csv file
    #     """
    #     with open(f"readings_{self.meter_id}_{today}.csv", "w") as file:
    #         writer = csv.writer(file)

    #         for reading in readings:
    #             writer.writerow(reading)

    # def system_maintenance(self):

# TODO: this was for testing, clean later
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

    test_account.backup_daily_readings()
    test_account.archive_monthly_billing()
    print(test_account)