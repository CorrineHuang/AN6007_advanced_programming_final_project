from datetime import datetime

class MeterReading:
    def __init__(self, meter_id, date, time, electricity_reading):
        self.meter_id = meter_id
        self.date = date # yyyy/mm/dd
        self.time = time # hh:mm
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

    @classmethod
    def validate_and_create(cls, meter_id, date, time, electricity_reading):
        """Validate and create a new MeterReading instance"""
        try:
            # Basic validation
            if not all([meter_id, date, time, electricity_reading]):
                raise ValueError("All fields are required")

            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except:
                raise ValueError('Invalid date format. Use YYYY-MM-DD')

            # Validate time format
            try:
                datetime.strptime(time, '%H:%M')
            except:
                raise ValueError('Invalid time format. Use HH:MM')

            # Validate electricity reading
            electricity_reading = float(electricity_reading)
            if electricity_reading < 0:
                raise ValueError("Electricity reading must be positive")

            # Create instance if all validations pass
            reading = cls(meter_id, date, time, electricity_reading)

            return reading

        except ValueError as e:
            raise ValueError(f"Validation failed: {str(e)}")