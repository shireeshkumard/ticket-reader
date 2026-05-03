# METAR Reader

A Flask web application that fetches live METAR weather reports for any airport and translates the cryptic shorthand into plain English.

## What is a METAR?

METAR is a standardized aviation weather format used by pilots and air traffic controllers worldwide. A raw report looks like this:

```
METAR KJFK 030351Z 36012KT 10SM BKN085 OVC250 12/M02 A2986
```

Not exactly readable. METAR Reader decodes it into:

> **Mostly cloudy at 8,500 ft, overcast at 25,000 ft — 53.6°F (12°C), wind 14 mph from the N (360°)**

## Features

- Enter any ICAO airport code (e.g. `KHIO`, `KJFK`, `EGLL`) to get a live weather report
- Decodes all major METAR fields:
  - Wind speed and direction (knots → mph, degrees → cardinal)
  - Visibility
  - Sky conditions with cloud layer altitudes
  - Weather phenomena (rain, snow, fog, thunderstorms, haze, and more)
  - Temperature and dewpoint in both °F and °C
  - Estimated relative humidity
  - Altimeter setting in inHg and hPa
- Shows the raw METAR alongside the decoded report
- Live data from the [FAA Aviation Weather Center API](https://aviationweather.gov/api/data/metar)

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/Scripts/activate     # Git Bash / macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

```
Metar_Reader/
  app.py              # Flask routes — fetches METAR from API, returns decoded JSON
  metar_decoder.py    # METAR parser — tokenizes and translates each field
  requirements.txt    # flask, requests
  templates/
    index.html        # Single-page UI
```
