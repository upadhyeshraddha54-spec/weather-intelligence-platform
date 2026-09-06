"""
FastAPI endpoint unit tests (no live network, no LLM calls).
Uses TestClient — no server needs to be running.
"""
import os
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app, raise_server_exceptions=False)


class TestHealthCheck:
    def test_root_returns_200(self):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_has_status_online(self):
        r = client.get("/")
        assert r.json()["status"] == "online"

    def test_root_has_components(self):
        r = client.get("/")
        data = r.json()
        assert "components" in data
        assert "ml_model" in data["components"]
        assert "dl_model" in data["components"]
        assert "cv_model" in data["components"]
        assert "llm" in data["components"]

    def test_root_ml_model_loaded(self):
        r = client.get("/")
        assert r.json()["components"]["ml_model"]["loaded"] is True


class TestMLPredict:
    def _valid_payload(self):
        return {
            "humidity": 72.0,
            "precip": 0.0,
            "month": 9,
            "day": 6,
            "dayofweek": 6,
            "season": 2,
        }

    def test_valid_input_returns_200(self):
        r = client.post("/predict", json=self._valid_payload())
        assert r.status_code == 200

    def test_returns_predicted_temperature_celsius(self):
        r = client.post("/predict", json=self._valid_payload())
        data = r.json()
        assert "predicted_temperature_celsius" in data
        assert isinstance(data["predicted_temperature_celsius"], float)

    def test_temperature_in_plausible_range(self):
        r = client.post("/predict", json=self._valid_payload())
        t = r.json()["predicted_temperature_celsius"]
        assert -20 <= t <= 60, f"Implausible temperature: {t}"

    def test_returns_model_key(self):
        r = client.post("/predict", json=self._valid_payload())
        assert "model" in r.json()

    def test_missing_field_returns_422(self):
        r = client.post("/predict", json={"humidity": 70.0})
        assert r.status_code == 422

    def test_all_seasons(self):
        for season in range(4):
            payload = self._valid_payload()
            payload["season"] = season
            r = client.post("/predict", json=payload)
            assert r.status_code == 200


class TestDLPredict:
    def _valid_sequence(self):
        """24 time steps × 6 features at mid-range values."""
        return {"sequence": [[28.0, 70.0, 0.0, 15.0, 9.0, 12.0]] * 24}

    def test_valid_input_returns_200_or_503(self):
        """Returns 200 (model loaded) or the untrained state dict."""
        r = client.post("/predict/dl", json=self._valid_sequence())
        assert r.status_code in (200, 503)

    def test_returns_status_key(self):
        r = client.post("/predict/dl", json=self._valid_sequence())
        if r.status_code == 200:
            assert "status" in r.json()

    def test_wrong_sequence_length_returns_422(self):
        r = client.post("/predict/dl", json={"sequence": [[28.0] * 6] * 5})
        assert r.status_code == 422

    def test_wrong_feature_count_returns_422(self):
        r = client.post("/predict/dl", json={"sequence": [[28.0, 70.0]] * 24})
        assert r.status_code == 422

    def test_untrained_does_not_fabricate(self):
        r = client.post("/predict/dl", json=self._valid_sequence())
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "untrained":
                assert data["predicted_temperature_celsius"] is None


class TestCVInfo:
    def test_returns_200(self):
        r = client.get("/cv/info")
        assert r.status_code == 200

    def test_has_architecture(self):
        r = client.get("/cv/info")
        assert "architecture" in r.json()

    def test_has_n_classes(self):
        r = client.get("/cv/info")
        assert r.json()["n_classes"] == 5


class TestDLInfo:
    def test_returns_200(self):
        r = client.get("/dl/info")
        assert r.status_code == 200

    def test_has_architecture(self):
        r = client.get("/dl/info")
        assert "architecture" in r.json()

    def test_status_valid(self):
        r = client.get("/dl/info")
        assert r.json()["status"] in ("ok", "untrained", "error")


class TestGeoEndpoint:
    def test_pune_returns_200(self):
        r = client.get("/geo/Pune")
        assert r.status_code == 200

    def test_pune_has_lat_lon(self):
        r = client.get("/geo/Pune")
        data = r.json()
        assert "latitude" in data
        assert "longitude" in data

    def test_pune_has_monsoon_zone(self):
        r = client.get("/geo/Pune")
        assert "monsoon_zone" in r.json()

    def test_pune_has_bounding_box(self):
        r = client.get("/geo/Pune")
        assert "bounding_box_50km" in r.json()

    def test_unknown_city_returns_404(self):
        r = client.get("/geo/xyznotacity99999")
        assert r.status_code == 404

    def test_mumbai_returns_200(self):
        r = client.get("/geo/Mumbai")
        assert r.status_code == 200


class TestAnalyzeEndpoint:
    """Smoke-tests that don't call external APIs — just verify schema."""

    def test_missing_city_returns_400(self):
        r = client.post("/analyze", json={"city": "", "question": "test"})
        assert r.status_code == 400

    def test_missing_question_returns_400(self):
        r = client.post("/analyze", json={"city": "Pune", "question": ""})
        assert r.status_code == 400

    def test_missing_body_returns_422(self):
        r = client.post("/analyze", json={})
        assert r.status_code == 422
