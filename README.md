# ⚡ Electricity Meter API

> A Flask-powered API for managing and analyzing electricity meter readings

## 🧰 Features

- **Retrieve All Readings**: Fetch all meter readings by meter ID.
- **Monthly Averages**: Calculate monthly average readings for specific meters.
- **User-Friendly Interface**: Test interface with clickable buttons for easy interaction.
- **Readable Responses**: Pretty JSON responses for better readability.

## 🗂️ Project Structure

```
├── app.py                     # Main Flask application
├── frontend_app.py            # Frontend interface for testing the API
├── meter_readings_generation.py  # Script to generate sample meter readings
├── utils.py                   # Utility functions for data processing
├── final.csv                  # Dataset containing meter readings
├── Assumptions.txt            # Project assumptions and considerations
├── REFERENCES.txt             # References and resources used
└── README.md                  # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Flask

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CorrineHuang/AN6007_advanced_programming_final_project.git
   ```


2. Navigate to the project directory:
   ```bash
   cd AN6007_advanced_programming_final_project
   ```


3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


### Running the Application

1. Start the Flask API:
   ```bash
   python app.py
   ```


2. Access the frontend interface:
   ```bash
   python frontend_app.py
   ```


3. Open your browser and navigate to `http://localhost:5000` to interact with the API.

## 📊 API Endpoints

- **GET /readings/&lt;meter_id&gt;**: Retrieve all readings for a specific meter.
- **GET /readings/&lt;meter_id&gt;/monthly-average**: Get monthly average readings for a specific meter.

## 📄 Additional Information

- **Assumptions**: Detailed in `Assumptions.txt`, outlining the project's scope and limitations.
- **References**: Listed in `REFERENCES.txt`, including all external resources and inspirations.

## 👩‍💻 Authors

- Corrine Huang，Joasy，Chunzie，Limey and Wwq.
