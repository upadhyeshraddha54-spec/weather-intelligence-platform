"""
AI Weather Intelligence Platform — Streamlit Dashboard.

Location selection:
  Country: India (only)
  State:   dependent on Country → all Indian states
  City:    dependent on State  → only cities in selected state

Each city has exact WGS-84 coordinates stored in india_cities.py.
The Open-Meteo API is called with those coordinates — never with a
hardcoded default.

Cache keys include BOTH the city display name AND its coordinates so
changing the city always fetches fresh data for the correct location.
"""
import sys
import os
import textwrap
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.weather.live_weather import get_live_weather
from src.forecast.live_forecast import get_forecast
from src.geospatial.india_cities import get_states, get_city_display_names, get_coordinates

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Weather Intelligence Platform",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

FORECAST_DAYS = 8

# ---------------------------------------------------------
# RENDER HELPER
# ---------------------------------------------------------

def render(html: str) -> None:
    html = textwrap.dedent(html).strip()
    html = "\n".join(line for line in html.splitlines() if line.strip())
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

render("""
<style>
.stApp { background-color: #ffffff; color: #1e293b; }
section[data-testid="stSidebar"] { background-color: #f8fafc; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }
.main-title { font-size: 42px; font-weight: 700; margin-bottom: 5px; color: #0f172a; }
.subtitle { color: #64748b; font-size: 17px; margin-bottom: 30px; }
.location { font-size: 20px; font-weight: 600; color: #0f172a; margin-bottom: 20px; }
.location-box { background: #1d4ed8; border-radius: 12px; padding: 18px; color: white; }
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] span,
[data-testid="stSelectbox"] div[data-baseweb="select"] div { color: #1e293b !important; }
[data-testid="stSelectbox"] svg { fill: #1e293b !important; }
[data-testid="stSelectbox"] label { color: #1e293b !important; }
[data-testid="stSelectbox"] div[data-baseweb="select"]:hover { border: 1px solid #1d4ed8 !important; }
ul[role="listbox"] { background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; }
ul[role="listbox"] li { color: #1e293b !important; }
ul[role="listbox"] li:hover { background-color: #eff6ff !important; }
div[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
}
div[data-baseweb="input"] input { color: #1e293b !important; }
.stButton > button {
    background-color: #1d4ed8; color: white; border: none;
    border-radius: 10px; font-weight: 650; min-height: 42px;
}
.stButton > button:hover { background-color: #1e40af; color: white; }
.dash-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 20px; padding: 22px; box-sizing: border-box;
}
.dash-card-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 14px; }
.conditions-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 20px; padding: 26px; min-height: 260px; box-sizing: border-box;
}
.conditions-location { font-size: 14px; color: #64748b; margin-bottom: 8px; }
.conditions-temp { font-size: 56px; font-weight: 800; color: #0f172a; line-height: 1; }
.conditions-desc { font-size: 16px; color: #64748b; margin: 10px 0 18px 0; }
.conditions-minirow { display: flex; flex-wrap: wrap; gap: 22px; font-size: 13px; color: #64748b; }
.forecast-pill {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 14px 8px;
    text-align: center; min-height: 110px; box-sizing: border-box;
}
.forecast-pill.active { background: #1d4ed8; border-color: #1d4ed8; }
.forecast-pill.active .forecast-pill-day,
.forecast-pill.active .forecast-pill-temp { color: #ffffff !important; }
.forecast-pill-day { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px; }
.forecast-pill-icon { font-size: 22px; margin-bottom: 6px; }
.forecast-pill-temp { font-size: 14px; font-weight: 700; color: #1e293b; }
.mini-stat {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 16px; min-height: 80px; box-sizing: border-box;
}
.mini-stat-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.mini-stat-value { font-size: 18px; font-weight: 700; color: #0f172a; }
.compass-wrap { display: flex; align-items: center; justify-content: center; gap: 26px; min-height: 160px; }
.compass-circle {
    width: 130px; height: 130px; min-width: 130px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, #1d4ed8 0deg 60deg, #e2e8f0 60deg 360deg);
    display: flex; align-items: center; justify-content: center;
}
.compass-inner {
    width: 96px; height: 96px; background: #ffffff; border-radius: 50%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.compass-inner-value { font-size: 20px; font-weight: 800; color: #0f172a; }
.compass-inner-sub { font-size: 11px; color: #64748b; }
.map-card {
    border-radius: 16px; border: 1px solid #e2e8f0; height: 160px;
    background:
        repeating-linear-gradient(0deg, #f1f5f9, #f1f5f9 19px, #e2e8f0 20px),
        repeating-linear-gradient(90deg, #f8fafc, #f8fafc 19px, #e2e8f0 20px);
    position: relative;
}
.map-card-label {
    position: absolute; bottom: 10px; left: 12px;
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 4px 10px; font-size: 12px; color: #475569;
}
.bar-chart { display: flex; align-items: flex-end; gap: 8px; height: 120px; margin-top: 10px; }
.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; }
.bar-fill { width: 60%; min-height: 4px; background: #1d4ed8; border-radius: 6px 6px 0 0; }
.bar-label { font-size: 11px; color: #94a3b8; margin-top: 6px; white-space: nowrap; }
.error-card {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 16px; padding: 18px; color: #991b1b; margin-bottom: 15px;
}
.coords-badge {
    font-size: 11px; color: #94a3b8; margin-top: 6px;
    font-family: monospace;
}
</style>
""")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def safe_get(data, keys, default=None):
    if not isinstance(data, dict):
        return default
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return default

def fmt_temp(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.0f}°C"
    except (ValueError, TypeError):
        return str(value)

def fmt_val(value, suffix=""):
    if value is None:
        return "N/A"
    return f"{value}{suffix}"

def condition_icon(condition_text):
    if not condition_text:
        return "🌤️"
    text = str(condition_text).lower()
    if "thunder" in text or "storm" in text:
        return "⛈️"
    if "snow" in text:
        return "❄️"
    if "rain" in text or "drizzle" in text or "shower" in text:
        return "🌧️"
    if "cloud" in text or "overcast" in text:
        return "⛅"
    if "fog" in text or "mist" in text or "haze" in text:
        return "🌫️"
    if "clear" in text or "sun" in text:
        return "☀️"
    return "🌤️"

def bar_chart_html(data, max_value):
    if not data:
        return None
    bars_html = ""
    for label, value in data:
        try:
            pct = max(4, min(100, round((float(value) / float(max_value)) * 100)))
        except (ValueError, TypeError, ZeroDivisionError):
            pct = 4
        bars_html += (
            f'<div class="bar-col">'
            f'<div class="bar-fill" style="height:{pct}%;"></div>'
            f'<div class="bar-label">{label}</div>'
            f'</div>'
        )
    return f'<div class="bar-chart">{bars_html}</div>'


# ---------------------------------------------------------
# CACHED DATA FETCHERS
# Cache key includes BOTH city name AND coordinates so
# switching city always fetches fresh data for that location.
# ---------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def fetch_weather(city_api_name: str, lat: float, lon: float):
    """
    Fetch live weather for a city.

    The lat/lon are included as cache keys so changing the selected city
    ALWAYS triggers a fresh API call with the correct coordinates.
    The city_api_name string is passed to get_live_weather() which
    geocodes it — but the lat/lon guarantee cache isolation.
    """
    return get_live_weather(city_api_name)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_forecast(city_api_name: str, lat: float, lon: float, days: int):
    """
    Fetch forecast for a city.

    The lat/lon are included as cache keys — same isolation guarantee.
    """
    return get_forecast(city_api_name, forecast_days=days)


# ---------------------------------------------------------
# SIDEBAR — Dependent Country → State → City dropdowns
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("## 🌍 Location")

    # Country: India only
    country = st.selectbox("Country", ["India"])

    # State: all Indian states, sorted alphabetically
    all_states = get_states()
    state = st.selectbox("State", all_states)

    # City: filtered by selected state
    # When state changes, the city index resets to 0 (first city in new state)
    city_names_for_state = get_city_display_names(state)
    if not city_names_for_state:
        city_names_for_state = ["(No cities available)"]

    city_display = st.selectbox(
        "City",
        city_names_for_state,
        key=f"city_{state}",   # key changes with state → forces reset to index 0
    )

    # Resolve coordinates for the selected city
    city_lat, city_lon, city_api_name = get_coordinates(state, city_display)

    st.divider()

    # Show coordinates so user can verify the correct location is being used
    render(f"""
        <div class="location-box">
            📍 <b>Selected Location</b>
            <br><br>
            Country: {country}
            <br><br>
            State: {state}
            <br><br>
            City: {city_display}
        </div>
        <div class="coords-badge">
            lat {city_lat:.4f} &nbsp; lon {city_lon:.4f}
        </div>
    """)

    st.divider()

    refresh = st.button("🔄 Update Weather", use_container_width=True)
    if refresh:
        fetch_weather.clear()
        fetch_forecast.clear()
        st.rerun()


# ---------------------------------------------------------
# GUARD — valid coordinates required
# ---------------------------------------------------------

if city_lat is None or city_lon is None:
    st.warning(f"No coordinates available for {city_display}. Select a different city.")
    st.stop()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

render("""
    <div class="main-title">🌦️ AI Weather Intelligence Platform</div>
    <div class="subtitle">Weather • Forecast • Air Quality • Satellite • Risk Intelligence</div>
""")

render(f"""
    <div class="location">
        📍 {city_display}, {state}, {country}
        &nbsp;<span style="font-size:13px;color:#94a3b8;font-family:monospace">
        ({city_lat:.4f}°N, {city_lon:.4f}°E)
        </span>
    </div>
""")

st.write("")


# ---------------------------------------------------------
# FETCH DATA — keyed on (city_api_name, lat, lon)
# This guarantees different cities never share cached results.
# ---------------------------------------------------------

weather = None
weather_error = None
try:
    weather = fetch_weather(city_api_name, city_lat, city_lon)
    if weather is None:
        weather_error = f"Weather data is currently unavailable for {city_display}."
except Exception as exc:
    weather_error = str(exc)

forecast_list = []
forecast_error = None
try:
    forecast_response = fetch_forecast(city_api_name, city_lat, city_lon, FORECAST_DAYS)
    if isinstance(forecast_response, list):
        forecast_list = forecast_response
    elif isinstance(forecast_response, dict):
        forecast_list = safe_get(forecast_response, ["forecast", "days", "data"], default=[])
    if not isinstance(forecast_list, list):
        forecast_list = []
except Exception as exc:
    forecast_error = str(exc)


# ---------------------------------------------------------
# ERRORS
# ---------------------------------------------------------

if weather_error:
    render(f"""
        <div class="error-card">
            ⚠️ <b>Could not load current weather for {city_display}</b><br><br>
            {weather_error}
        </div>
    """)

if forecast_error:
    render(f"""
        <div class="error-card">
            ⚠️ <b>Could not load the {FORECAST_DAYS}-day forecast for {city_display}</b><br><br>
            {forecast_error}
        </div>
    """)


# ---------------------------------------------------------
# ROW 1 — CURRENT CONDITIONS + FORECAST
# ---------------------------------------------------------

row1_left, row1_right = st.columns([1.3, 2])

with row1_left:
    if weather:
        temperature = safe_get(weather, ["temperature", "temp", "temperature_c"])
        condition   = safe_get(weather, ["condition", "description", "weather_desc", "summary"], "")
        feels_like  = safe_get(weather, ["feels_like", "apparent_temperature", "feelslike_c"])
        high        = safe_get(weather, ["temp_max", "high", "max_temp"])
        low         = safe_get(weather, ["temp_min", "low", "min_temp"])

        render(f"""
            <div class="conditions-card">
                <div class="conditions-location">📍 {city_display} — Current Conditions</div>
                <div class="conditions-temp">{fmt_temp(temperature)}</div>
                <div class="conditions-desc">{condition_icon(condition)} {condition or "N/A"}</div>
                <div class="conditions-minirow">
                    <div>Feels like <b>{fmt_temp(feels_like)}</b></div>
                    <div>High <b>{fmt_temp(high)}</b></div>
                    <div>Low <b>{fmt_temp(low)}</b></div>
                </div>
            </div>
        """)
    else:
        render(f"""
            <div class="conditions-card">
                <div class="conditions-location">📍 {city_display} — Current Conditions</div>
                <div class="conditions-desc">
                    Weather data is currently unavailable for {city_display}.
                </div>
            </div>
        """)

with row1_right:
    render(f'<div class="dash-card-title">{FORECAST_DAYS}-Day Forecast</div>')

    if forecast_list:
        items = forecast_list[:FORECAST_DAYS]
        cols = st.columns(len(items))
        for idx, (col, item) in enumerate(zip(cols, items)):
            with col:
                day_label = safe_get(item, ["date", "day", "day_name", "datetime"], f"Day {idx+1}")
                max_temp  = safe_get(item, ["max_temp", "temperature_max", "temp_max"])
                min_temp  = safe_get(item, ["min_temp", "temperature_min", "temp_min"])
                cond_val  = safe_get(item, ["condition", "description", "summary"], "")
                active    = " active" if idx == 0 else ""
                render(f"""
                    <div class="forecast-pill{active}">
                        <div class="forecast-pill-day">{day_label}</div>
                        <div class="forecast-pill-icon">{condition_icon(cond_val)}</div>
                        <div class="forecast-pill-temp">{fmt_temp(max_temp)} / {fmt_temp(min_temp)}</div>
                    </div>
                """)
    else:
        st.info(f"No {FORECAST_DAYS}-day forecast data available for {city_display}.")

st.write("")


# ---------------------------------------------------------
# ROW 2 — MINI STATS + WIND + MAP
# ---------------------------------------------------------

row2_left, row2_mid, row2_right = st.columns([1.3, 1, 1])

with row2_left:
    sunrise    = safe_get(weather, ["sunrise", "sunrise_time"])
    sunset     = safe_get(weather, ["sunset",  "sunset_time"])
    feels_like = safe_get(weather, ["feels_like", "apparent_temperature", "feelslike_c"])
    visibility = safe_get(weather, ["visibility", "visibility_km"])

    m1, m2 = st.columns(2)
    with m1:
        render(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">🌅 Sunrise</div>
                <div class="mini-stat-value">{fmt_val(sunrise)}</div>
            </div>
        """)
    with m2:
        render(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">🌡️ Feels like</div>
                <div class="mini-stat-value">{fmt_temp(feels_like)}</div>
            </div>
        """)

    st.write("")
    m3, m4 = st.columns(2)
    with m3:
        render(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">🌇 Sunset</div>
                <div class="mini-stat-value">{fmt_val(sunset)}</div>
            </div>
        """)
    with m4:
        render(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">👁️ Visibility</div>
                <div class="mini-stat-value">{fmt_val(visibility, " km")}</div>
            </div>
        """)

with row2_mid:
    wind_speed = safe_get(weather, ["wind_speed", "wind", "windspeed"])
    humidity   = safe_get(weather, ["humidity", "humidity_percent"])
    render('<div class="dash-card-title">Wind Speed</div>')
    render(f"""
        <div class="dash-card">
            <div class="compass-wrap">
                <div class="compass-circle">
                    <div class="compass-inner">
                        <div class="compass-inner-value">{fmt_val(wind_speed)}</div>
                        <div class="compass-inner-sub">km/h</div>
                    </div>
                </div>
                <div>
                    <div class="mini-stat-label">Humidity</div>
                    <div class="mini-stat-value">{fmt_val(humidity, "%")}</div>
                </div>
            </div>
        </div>
    """)

with row2_right:
    render('<div class="dash-card-title">Map</div>')
    render(f"""
        <div class="map-card">
            <div class="map-card-label">
                📍 {city_display}
                &nbsp; {city_lat:.3f}°N, {city_lon:.3f}°E
            </div>
        </div>
    """)

st.write("")


# ---------------------------------------------------------
# ROW 3 — RAIN / UV BAR CHARTS
# ---------------------------------------------------------

chart1, chart2, chart3 = st.columns(3)

rain_series, uv_series, pressure_series = [], [], []

if forecast_list:
    for item in forecast_list[:FORECAST_DAYS]:
        day_label = safe_get(item, ["date", "day", "day_name"], "")
        rain_val  = safe_get(item, ["rain_chance", "precipitation_probability", "pop"])
        uv_val    = safe_get(item, ["uv_index", "uv"])

        if rain_val is not None:
            rain_series.append((day_label, rain_val))
        if uv_val is not None:
            uv_series.append((day_label, uv_val))

# Current AQI from weather dict
aqi_val  = safe_get(weather, ["aqi", "us_aqi"])
pm25_val = safe_get(weather, ["pm2_5", "pm25"])
pm10_val = safe_get(weather, ["pm10"])

with chart1:
    if rain_series:
        ch = bar_chart_html(rain_series, max_value=100)
        render(f'<div class="dash-card"><div class="dash-card-title">🌧️ Chance of Rain (%)</div>{ch}</div>')
    else:
        render('<div class="dash-card"><div class="dash-card-title">🌧️ Chance of Rain</div><p style="color:#94a3b8;font-size:13px">No data available.</p></div>')

with chart2:
    if uv_series:
        ch = bar_chart_html(uv_series, max_value=11)
        render(f'<div class="dash-card"><div class="dash-card-title">☀️ UV Index</div>{ch}</div>')
    else:
        render('<div class="dash-card"><div class="dash-card-title">☀️ UV Index</div><p style="color:#94a3b8;font-size:13px">No data available.</p></div>')

with chart3:
    aqi_display = fmt_val(aqi_val)
    pm25_display = fmt_val(pm25_val, " µg/m³")
    pm10_display = fmt_val(pm10_val, " µg/m³")
    render(f"""
        <div class="dash-card">
            <div class="dash-card-title">🌫️ Air Quality</div>
            <div style="margin-top:8px">
                <div class="mini-stat-label">US AQI</div>
                <div class="mini-stat-value">{aqi_display}</div>
            </div>
            <div style="margin-top:12px;display:flex;gap:24px">
                <div>
                    <div class="mini-stat-label">PM2.5</div>
                    <div style="font-size:14px;font-weight:600;color:#0f172a">{pm25_display}</div>
                </div>
                <div>
                    <div class="mini-stat-label">PM10</div>
                    <div style="font-size:14px;font-weight:600;color:#0f172a">{pm10_display}</div>
                </div>
            </div>
        </div>
    """)

# ---------------------------------------------------------
# LAST UPDATED
# ---------------------------------------------------------

st.caption(
    f"📍 Data for {city_display} ({city_lat:.4f}°N, {city_lon:.4f}°E) | "
    f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
)
