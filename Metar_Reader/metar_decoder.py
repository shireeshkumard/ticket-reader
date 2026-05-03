import re
from datetime import datetime, timezone


WEATHER_PHENOMENA = {
    'DZ': 'drizzle', 'RA': 'rain', 'SN': 'snow', 'SG': 'snow grains',
    'IC': 'ice crystals', 'PL': 'ice pellets', 'GR': 'hail',
    'GS': 'small hail', 'BR': 'mist', 'FG': 'fog', 'FU': 'smoke',
    'VA': 'volcanic ash', 'DU': 'dust', 'SA': 'sand', 'HZ': 'haze',
    'PO': 'dust devils', 'SQ': 'squalls', 'FC': 'funnel cloud / tornado',
    'SS': 'sandstorm', 'DS': 'dust storm',
}

WEATHER_DESCRIPTORS = {
    'MI': 'shallow', 'PR': 'partial', 'BC': 'patchy',
    'DR': 'low drifting', 'BL': 'blowing', 'SH': 'showers of',
    'TS': 'thunderstorm with', 'FZ': 'freezing',
}

SKY_COVER = {
    'SKC': 'clear', 'CLR': 'clear', 'NCD': 'clear', 'NSC': 'no significant clouds',
    'CAVOK': 'clear, visibility OK',
    'FEW': 'a few clouds', 'SCT': 'scattered clouds',
    'BKN': 'mostly cloudy', 'OVC': 'overcast', 'VV': 'sky obscured',
}

INTENSITY_LABELS = {'-': 'light', '': 'moderate', '+': 'heavy', 'VC': 'nearby'}


def _deg_to_cardinal(deg):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    return dirs[round(deg / 22.5) % 16]


def _c_to_f(c):
    return round(c * 9 / 5 + 32, 1)


def _knots_to_mph(kt):
    return round(kt * 1.15078)


def _parse_temp(token):
    """Parse M02 → -2, 15 → 15."""
    if token.startswith('M'):
        return -int(token[1:])
    return int(token)


def _parse_wind(token):
    m = re.match(r'^(VRB|\d{3})(\d{2,3})(G(\d{2,3}))?KT$', token)
    if not m:
        return None
    direction_raw, speed_raw, _, gust_raw = m.groups()
    speed_kt = int(speed_raw)
    gust_kt = int(gust_raw) if gust_raw else None
    speed_mph = _knots_to_mph(speed_kt)
    gust_mph = _knots_to_mph(gust_kt) if gust_kt else None

    if direction_raw == 'VRB' or speed_kt == 0:
        direction_str = 'variable direction' if direction_raw == 'VRB' else None
        if speed_kt == 0:
            return {'text': 'Calm winds', 'calm': True}
        cardinal = 'variable'
    else:
        deg = int(direction_raw)
        cardinal = _deg_to_cardinal(deg)
        direction_str = f'{cardinal} ({deg}°)'

    parts = [f'{speed_mph} mph']
    if gust_mph:
        parts.append(f'gusting to {gust_mph} mph')
    wind_speed_str = ' '.join(parts)

    if direction_raw == 'VRB':
        text = f'Variable direction at {wind_speed_str}'
    else:
        deg = int(direction_raw)
        cardinal = _deg_to_cardinal(deg)
        text = f'{wind_speed_str} from the {cardinal} ({deg}°)'

    return {'text': text, 'speed_mph': speed_mph, 'gust_mph': gust_mph,
            'cardinal': cardinal if direction_raw != 'VRB' else 'variable',
            'calm': False}


def _parse_visibility(token):
    if token == 'CAVOK':
        return 'Unlimited (CAVOK)'
    m = re.match(r'^(M?)(\d+(?:/\d+)?)SM$', token)
    if not m:
        return None
    less_than, vis = m.groups()
    prefix = 'Less than ' if less_than else ''
    if '/' in vis:
        num, denom = vis.split('/')
        miles = int(num) / int(denom)
        return f'{prefix}{vis} mile' + ('' if miles == 1 else 's')
    return f'{prefix}{vis} mile' + ('' if vis == "1" else 's')


def _parse_sky(tokens):
    layers = []
    clear = False
    for token in tokens:
        if token in ('SKC', 'CLR', 'NCD', 'NSC', 'CAVOK'):
            clear = True
            layers.append(SKY_COVER[token])
            continue
        m = re.match(r'^(FEW|SCT|BKN|OVC|VV)(\d{3})(CB|TCU)?$', token)
        if not m:
            continue
        cover, height_code, cloud_type = m.groups()
        height_ft = int(height_code) * 100
        label = SKY_COVER.get(cover, cover)
        suffix = ''
        if cloud_type == 'CB':
            suffix = ' with cumulonimbus (thunderstorm potential)'
        elif cloud_type == 'TCU':
            suffix = ' with towering cumulus'
        layers.append(f'{label.capitalize()} at {height_ft:,} ft{suffix}')
    return layers, clear


def _parse_weather(token):
    token_orig = token
    intensity = ''
    if token.startswith('+'):
        intensity = '+'
        token = token[1:]
    elif token.startswith('-'):
        intensity = '-'
        token = token[1:]
    elif token.startswith('VC'):
        intensity = 'VC'
        token = token[2:]

    descriptor = ''
    for key in WEATHER_DESCRIPTORS:
        if token.startswith(key) and key != 'TS':
            descriptor = key
            token = token[len(key):]
            break

    ts_descriptor = ''
    if token.startswith('TS') and 'TS' not in descriptor:
        ts_descriptor = 'TS'
        token = token[2:]

    phenomena = []
    while token:
        matched = False
        for key in sorted(WEATHER_PHENOMENA.keys(), key=len, reverse=True):
            if token.startswith(key):
                phenomena.append(WEATHER_PHENOMENA[key])
                token = token[len(key):]
                matched = True
                break
        if not matched:
            break

    if not phenomena and not ts_descriptor:
        return None

    parts = []
    if intensity:
        parts.append(INTENSITY_LABELS.get(intensity, intensity))
    if descriptor:
        parts.append(WEATHER_DESCRIPTORS[descriptor])
    if ts_descriptor:
        parts.append('thunderstorm with')
    parts.extend(phenomena)
    return ' '.join(parts).strip().capitalize()


def decode(raw_metar):
    raw = raw_metar.strip().rstrip('$').strip()
    tokens = raw.split()
    if not tokens:
        return {'error': 'Empty METAR'}

    result = {
        'raw': raw,
        'station': None,
        'time_utc': None,
        'auto': False,
        'wind': None,
        'wind_variable_range': None,
        'visibility': None,
        'weather': [],
        'sky_layers': [],
        'sky_clear': False,
        'temp_c': None,
        'temp_f': None,
        'dewpoint_c': None,
        'dewpoint_f': None,
        'altimeter_inhg': None,
        'altimeter_hpa': None,
        'summary': '',
        'warnings': [],
    }

    idx = 0

    # Station
    if re.match(r'^[A-Z]{3,4}$', tokens[idx]):
        result['station'] = tokens[idx]
        idx += 1

    # Skip METAR prefix if present
    if idx < len(tokens) and tokens[idx] == 'METAR':
        idx += 1
        if idx < len(tokens) and re.match(r'^[A-Z]{3,4}$', tokens[idx]):
            result['station'] = tokens[idx]
            idx += 1

    # Time
    if idx < len(tokens) and re.match(r'^\d{6}Z$', tokens[idx]):
        t = tokens[idx]
        day, hour, minute = int(t[0:2]), int(t[2:4]), int(t[4:6])
        now = datetime.now(timezone.utc)
        result['time_utc'] = f'Day {day} of month, {hour:02d}:{minute:02d} UTC'
        idx += 1

    # AUTO / COR
    if idx < len(tokens) and tokens[idx] in ('AUTO', 'COR'):
        result['auto'] = tokens[idx] == 'AUTO'
        idx += 1

    # Wind
    if idx < len(tokens) and re.match(r'^(VRB|\d{3})\d{2,3}(G\d{2,3})?KT$', tokens[idx]):
        result['wind'] = _parse_wind(tokens[idx])
        idx += 1

    # Variable wind direction range (e.g. 280V350)
    if idx < len(tokens) and re.match(r'^\d{3}V\d{3}$', tokens[idx]):
        a, b = tokens[idx].split('V')
        result['wind_variable_range'] = f'varying between {a}° and {b}°'
        idx += 1

    # Visibility — may be two tokens like "1 1/2SM"
    vis_tokens = []
    while idx < len(tokens):
        t = tokens[idx]
        if re.match(r'^(M?\d+(?:/\d+)?SM|CAVOK)$', t):
            vis_tokens.append(t)
            idx += 1
            # check if next is fractional continuation e.g. "1 1/2SM"
        elif vis_tokens and re.match(r'^\d+/\d+SM$', t):
            # combine "1" + "1/2SM" → handle as-is; already captured
            vis_tokens.append(t)
            idx += 1
            break
        else:
            break

    if vis_tokens:
        # If we got two tokens like "1" and "1/2SM", combine
        if len(vis_tokens) == 2 and re.match(r'^\d+$', vis_tokens[0].replace('SM', '')):
            whole = vis_tokens[0]
            frac_token = vis_tokens[1]
            m = re.match(r'^(M?)(\d+)/(\d+)SM$', frac_token)
            if m:
                less, num, denom = m.groups()
                total = int(whole) + int(num) / int(denom)
                result['visibility'] = f'{total:.2g} miles'
            else:
                result['visibility'] = _parse_visibility(vis_tokens[0])
        else:
            result['visibility'] = _parse_visibility(vis_tokens[0])

    # R-group (runway visual range) — skip
    while idx < len(tokens) and tokens[idx].startswith('R') and '/' in tokens[idx]:
        idx += 1

    # Weather phenomena
    weather_pattern = re.compile(
        r'^(VC|[-+])?'
        r'(MI|PR|BC|DR|BL|SH|TS|FZ)?'
        r'(TS)?'
        r'(DZ|RA|SN|SG|IC|PL|GR|GS|BR|FG|FU|VA|DU|SA|HZ|PO|SQ|FC|SS|DS)+'
        r'$'
    )
    while idx < len(tokens) and weather_pattern.match(tokens[idx]):
        decoded_wx = _parse_weather(tokens[idx])
        if decoded_wx:
            result['weather'].append(decoded_wx)
        idx += 1

    # Sky conditions
    sky_tokens = []
    while idx < len(tokens):
        t = tokens[idx]
        if re.match(r'^(FEW|SCT|BKN|OVC|VV)\d{3}(CB|TCU)?$', t) or t in ('SKC', 'CLR', 'NCD', 'NSC', 'CAVOK'):
            sky_tokens.append(t)
            idx += 1
        else:
            break
    if sky_tokens:
        layers, clear = _parse_sky(sky_tokens)
        result['sky_layers'] = layers
        result['sky_clear'] = clear

    # Temp / Dewpoint
    if idx < len(tokens) and re.match(r'^M?\d+/M?\d+$', tokens[idx]):
        temp_str, dew_str = tokens[idx].split('/')
        tc = _parse_temp(temp_str)
        dc = _parse_temp(dew_str)
        result['temp_c'] = tc
        result['temp_f'] = _c_to_f(tc)
        result['dewpoint_c'] = dc
        result['dewpoint_f'] = _c_to_f(dc)
        idx += 1

    # Altimeter
    if idx < len(tokens) and re.match(r'^A\d{4}$', tokens[idx]):
        inhg = int(tokens[idx][1:]) / 100
        result['altimeter_inhg'] = round(inhg, 2)
        result['altimeter_hpa'] = round(inhg * 33.8639, 1)
        idx += 1
    elif idx < len(tokens) and re.match(r'^Q\d{4}$', tokens[idx]):
        hpa = int(tokens[idx][1:])
        result['altimeter_hpa'] = hpa
        result['altimeter_inhg'] = round(hpa / 33.8639, 2)
        idx += 1

    # Build plain-English summary
    result['summary'] = _build_summary(result)
    return result


def _build_summary(r):
    parts = []

    # Sky / overall condition
    if r['weather']:
        parts.append(', '.join(r['weather']).capitalize())
    elif r['sky_clear']:
        parts.append('Clear skies')
    elif r['sky_layers']:
        # Use topmost (worst) layer for summary
        top = r['sky_layers'][-1].lower()
        parts.append(top.capitalize())

    # Temperature
    if r['temp_f'] is not None:
        parts.append(f'{r["temp_f"]}°F ({r["temp_c"]}°C)')

    # Wind
    if r['wind']:
        if r['wind'].get('calm'):
            parts.append('calm winds')
        else:
            parts.append(f'wind {r["wind"]["text"]}')

    # Visibility
    if r['visibility'] and r['visibility'] not in ('10 miles', 'Unlimited (CAVOK)'):
        parts.append(f'visibility {r["visibility"]}')

    return ', '.join(parts) if parts else 'Weather data decoded'
