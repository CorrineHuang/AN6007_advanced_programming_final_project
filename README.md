# ⚡ Electricity Meter API

> A Flask-powered API for managing and analyzing electricity meter readings 🌟

## 🎯 Features

- 📊 Get all meter readings by meter ID
- 📈 Calculate monthly averages for specific meters
- 🔍 Easy-to-use test interface with clickable buttons
- 🎨 Pretty JSON responses for better readability

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
