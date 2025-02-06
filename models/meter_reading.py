import datetime

class MeterReading:
    def __init__(self, meter_id, date, time, electricity_reading):
        self.meter_id = meter_id
        self.date = date # dd/mm/yyyy
        self.time = time # hh:mm:ss
        self.electricity_reading = electricity_reading # float

    def __str__(self):
        return (
            f"Meter Id: {self.meter_id}\n"
            f"Date: {self.date}\n"
            f"Time: {self.time}\n"
            f"Electricity Reading (kWh): {self.electricity_reading}\n"
        )

    def to_dict(self):
        """Convert the MeterReading object to a dictionary"""
        return {
            'meter_id': self.meter_id,
            'date': self.date,
            'time': self.time,
            'electricity_reading': self.electricity_reading
        }

    @classmethod
    def from_dict(cls, data):
        """Create an MeterReading instance from a dictionary"""
        return cls(
            meter_id=data.get('meter_id'),
            date=data.get('date'),
            time=data.get('time'),
            electricity_reading=data.get('electricity_reading')
        )