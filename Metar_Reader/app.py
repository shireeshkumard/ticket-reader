import requests
from flask import Flask, render_template, request, jsonify
from metar_decoder import decode

app = Flask(__name__)

METAR_API = 'https://aviationweather.gov/api/data/metar'


def fetch_metar(station_id):
    try:
        resp = requests.get(METAR_API, params={'ids': station_id.upper()}, timeout=10)
        resp.raise_for_status()
        text = resp.text.strip()
        if not text:
            return None, f'No METAR data found for {station_id.upper()}. Check the airport code and try again.'
        return text, None
    except requests.exceptions.ConnectionError:
        return None, 'Could not connect to the weather service. Check your internet connection.'
    except requests.exceptions.Timeout:
        return None, 'The weather service timed out. Try again in a moment.'
    except requests.exceptions.HTTPError as e:
        return None, f'Weather service error: {e}'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/decode', methods=['POST'])
def decode_metar():
    data = request.get_json()
    station = (data or {}).get('station', '').strip()
    if not station:
        return jsonify({'error': 'Please enter an airport code.'}), 400
    if len(station) > 6 or not station.replace(' ', '').isalnum():
        return jsonify({'error': 'Invalid airport code format.'}), 400

    raw, err = fetch_metar(station)
    if err:
        return jsonify({'error': err}), 400

    result = decode(raw)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
