# ⚡ Electricity Meter API

> A Flask-powered API for managing and analyzing electricity meter readings 🌟

## 🎯 Features

- 📊 Get all meter readings by meter ID
- 📈 Calculate monthly averages for specific meters
- 🔍 Easy-to-use test interface with clickable buttons
- 🎨 Pretty JSON responses for better readability

## Assumptions
- Server maintenance will only happen during 0000-0100.
- Meter will only be installed more than 1 hour before the start of server maintenance.
- When server crash, server recovery will start to run.
- When meter reading comes into the server is cumulative and positive number.
- The last line of csv in daily and monthly csv will be the latest reading.

## Installation Guide for Backend
- Step 1: Run this code in the terminal

```
python3 -m pip install --upgrade pip
```
- Step 2: Run this in the terminal
```
pip install -r requirements.txt
```
- Step 3: Run this in terminal
```
python app.py
```

- Step 4: Make server public
```
Make the port public in order to use reqbin.
```

## How to use the API

1. Run `python app.py` to start the server. Take note of the server URL, e.g `http://127.0.0.1:5000`/. If you are using Codespaces, the URL will be whatever the URL of your Codespaces is in the browser - it ends with `...github.dev/`, and you can append the rest of the API to the end, e.g. `github.dev/register`
2. Go to [reqbin](https://reqbin.com/#pills-req-content)
3. Send requests from reqbin.

**Register meter**

- Method: POST
- Type: JSON
- Body:

```
{
    "meter_id": "999-999-993",
    "area": "NTU",
    "region": "Jurong",
    "dwelling_type": "xyz"
}
```

**Meter reading**

- Method: POST
- Type: Form (url-encoded)
- Body:

```
meter_id=999-999-999
date=28-01-2020
time=14:30:11
electricity_reading=1000
```

## To be discussed
1. to be more user friendly,  do we need to add a dropdown list for users to choose? for dwelling-type, area and region.
![image](tools\image.png)

2. Need to add the Shiny/Dash thing in the 'More Analysis" button.

3. Do we need to add another API for monthly billing part?
And for 'calculate monthly usage', we calculate for this month or last month?