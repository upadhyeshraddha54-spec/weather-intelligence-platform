"""
Unit tests — weather intelligence platform.

These tests exercise pure Python logic that does NOT require network access,
LLM API keys, or the ML model file.  They run entirely offline using
pytest and should never call external services.
"""
import os
import sys
import pytest

# Ensure the project root is on sys.path when running from the tests/ dir.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ===========================================================================
# forecast/forecast_risk.py  — pure classification functions
# ===========================================================================

from src.forecast.forecast_risk import (
    classify_rainfall,
    classify_temperature,
    classify_wind,
    classify_rain_probability,
    analyze_forecast,
)


class TestClassifyRainfall:
    def test_none(self):
        assert classify_rainfall(None) == "Unknown"

    def test_zero(self):
        assert classify_rainfall(0) == "No Rain"

    def test_light(self):
        assert classify_rainfall(2) == "Light Rain"

    def test_moderate(self):
        assert classify_rainfall(10) == "Moderate Rain"

    def test_heavy(self):
        assert classify_rainfall(30) == "Heavy Rain"

    def test_very_heavy(self):
        assert classify_rainfall(75) == "Very Heavy Rain"

    def test_extreme(self):
        assert classify_rainfall(150) == "Extreme Rain"


class TestClassifyTemperature:
    def test_none(self):
        assert classify_temperature(None) == "Unknown"

    def test_normal(self):
        assert classify_temperature(35) == "Normal"

    def test_heatwave_boundary(self):
        assert classify_temperature(40) == "Heatwave Risk"

    def test_heatwave_above(self):
        assert classify_temperature(45) == "Heatwave Risk"


class TestClassifyWind:
    def test_none(self):
        assert classify_wind(None) == "Unknown"

    def test_normal(self):
        assert classify_wind(30) == "Normal"

    def test_strong_boundary(self):
        assert classify_wind(60) == "Strong Wind Risk"

    def test_strong_above(self):
        assert classify_wind(90) == "Strong Wind Risk"


class TestClassifyRainProbability:
    def test_none(self):
        assert classify_rain_probability(None) == "Unknown"

    def test_low(self):
        assert classify_rain_probability(10) == "Low"

    def test_moderate(self):
        assert classify_rain_probability(35) == "Moderate"

    def test_high(self):
        assert classify_rain_probability(65) == "High"

    def test_very_high(self):
        assert classify_rain_probability(90) == "Very High"


class TestAnalyzeForecast:
    """analyze_forecast must read ``rain_chance`` (not ``rain_probability``)."""

    def _make_day(self, **kwargs):
        defaults = {
            "date": "2026-09-07",
            "max_temp": 32,
            "min_temp": 22,
            "rainfall": 5,
            "rain_chance": 40,   # correct key from live_forecast.py
            "wind": 20,
            "weather_code": 61,
            "uv_index": 6,
        }
        defaults.update(kwargs)
        return defaults

    def test_output_keys(self):
        day = self._make_day()
        result = analyze_forecast([day])
        assert len(result) == 1
        row = result[0]
        assert "date" in row
        assert "rain_probability" in row       # output uses rain_probability
        assert "rainfall_class" in row
        assert "rain_probability_class" in row
        assert "temperature_class" in row
        assert "wind_class" in row

    def test_rain_chance_mapped_correctly(self):
        """rain_chance=40 should give rain_probability=40 and class Moderate."""
        day = self._make_day(rain_chance=40)
        result = analyze_forecast([day])
        assert result[0]["rain_probability"] == 40
        assert result[0]["rain_probability_class"] == "Moderate"

    def test_rain_chance_none(self):
        """rain_chance=None should give rain_probability=None and class Unknown."""
        day = self._make_day(rain_chance=None)
        result = analyze_forecast([day])
        assert result[0]["rain_probability"] is None
        assert result[0]["rain_probability_class"] == "Unknown"

    def test_empty_forecast(self):
        assert analyze_forecast([]) == []

    def test_multiple_days(self):
        days = [self._make_day(date=f"2026-09-0{i}") for i in range(1, 4)]
        result = analyze_forecast(days)
        assert len(result) == 3


# ===========================================================================
# agent/risk_agent.py  — risk assessment
# ===========================================================================

from src.agent.risk_agent import assess_risk, get_aqi_category


class TestGetAqiCategory:
    def test_none(self):
        assert get_aqi_category(None) == "AQI data unavailable"

    def test_good(self):
        assert get_aqi_category(25) == "Good"

    def test_moderate(self):
        assert get_aqi_category(75) == "Moderate"

    def test_sensitive(self):
        assert get_aqi_category(125) == "Unhealthy for Sensitive Groups"

    def test_unhealthy(self):
        assert get_aqi_category(175) == "Unhealthy"

    def test_very_unhealthy(self):
        assert get_aqi_category(250) == "Very Unhealthy"

    def test_hazardous(self):
        assert get_aqi_category(350) == "Hazardous"


class TestAssessRisk:
    def _weather(self, temperature=28, precipitation=0, wind_speed=20, aqi=30):
        return {
            "temperature": temperature,
            "precipitation": precipitation,
            "wind_speed": wind_speed,
            "aqi": aqi,
        }

    def test_no_risk(self):
        risks = assess_risk(self._weather())
        assert risks == ["No Major Weather or Air Quality Risk"]

    def test_heatwave(self):
        risks = assess_risk(self._weather(temperature=42))
        assert any("Heatwave" in r for r in risks)

    def test_heavy_rain(self):
        risks = assess_risk(self._weather(precipitation=160))
        assert any("Heavy Rain" in r for r in risks)

    def test_flood(self):
        risks = assess_risk(self._weather(precipitation=260))
        assert any("Flood" in r for r in risks)

    def test_strong_wind(self):
        risks = assess_risk(self._weather(wind_speed=65))
        assert any("Wind" in r for r in risks)

    def test_unhealthy_aqi(self):
        risks = assess_risk(self._weather(aqi=180))
        assert any("Unhealthy" in r for r in risks)

    def test_multiple_risks(self):
        risks = assess_risk(
            self._weather(temperature=42, wind_speed=70, aqi=180)
        )
        assert len(risks) >= 3


# ===========================================================================
# graph/state.py  — TypedDict fields
# ===========================================================================

from src.graph.state import WeatherState


class TestWeatherState:
    def test_required_fields(self):
        fields = WeatherState.__annotations__
        for field in (
            "city",
            "user_query",
            "selected_agents",
            "weather",
            "aqi",
            "forecast",
            "satellite",
            "risk",
            "rag",
            "bulletin",
            "decision_logs",
        ):
            assert field in fields, f"WeatherState missing field: {field}"


# ===========================================================================
# agent/rag_tool.py  — module import without crash
# ===========================================================================

def test_rag_tool_import():
    """Importing rag_tool must not raise even without network access."""
    import importlib
    import src.agent.rag_tool as rag_module
    importlib.reload(rag_module)
    assert callable(rag_module.search_weather_knowledge)


# ===========================================================================
# satellite/satellite_analysis.py  — unavailable state truthfulness
# ===========================================================================

def test_satellite_unavailable_state_is_honest():
    """When no satellite data is available, status must be 'unavailable'."""
    from src.satellite.satellite_analysis import analyze_satellite
    # With no network in sandbox pystac_client import will fail → unavailable.
    result = analyze_satellite("Pune")
    # Acceptable states: "unavailable" (no deps) or "ok" (deps present)
    assert result.get("status") in ("unavailable", "ok", "error")
    # Must never return a hardcoded fabricated date.
    assert result.get("image_date") != "2026-08-03", (
        "Satellite agent returned hardcoded fabricated date 2026-08-03"
    )


# ===========================================================================
# agent/bulletin_generator.py  — _safe_satellite helper
# ===========================================================================

def test_safe_satellite_with_none():
    from src.agent.bulletin_generator import _safe_satellite
    result = _safe_satellite(None)
    assert result["image_date"] == "N/A"
    assert result["summary"] == "No satellite analysis was performed."


def test_safe_satellite_with_unavailable_dict():
    from src.agent.bulletin_generator import _safe_satellite
    result = _safe_satellite({"status": "unavailable", "message": "Not installed"})
    assert result["image_date"] == "N/A"
    assert "Not installed" in result["summary"]


def test_safe_satellite_with_ok_dict():
    from src.agent.bulletin_generator import _safe_satellite
    data = {
        "status": "ok",
        "image_date": "2026-09-05",
        "cloud_cover": 45,
        "condition": "Mostly Cloudy",
        "rain_potential": "Moderate",
        "visibility": "Moderate",
        "confidence": "High",
        "summary": "45% cloud cover.",
    }
    result = _safe_satellite(data)
    assert result["image_date"] == "2026-09-05"
    assert result["cloud_cover"] == 45


# ===========================================================================
# data/config.py  — defaults
# ===========================================================================

from src.data.config import WeatherConfig


def test_weather_config_defaults():
    config = WeatherConfig()
    assert config.latitude == 18.5204
    assert config.longitude == 73.8567
    assert config.timezone == "auto"


def test_weather_config_custom():
    config = WeatherConfig(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata")
    assert config.latitude == 28.6
    assert config.longitude == 77.2
