"""
Unit tests for the Deep Learning (LSTM) module.

These tests do NOT require the trained weights file.
They verify architecture, I/O shapes, and the honest untrained state.
"""
import os
import sys
import numpy as np
import pytest
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.dl.lstm_model import (
    WeatherLSTM,
    normalise,
    denormalise_temperature,
    predict_next_temperature,
    get_model_info,
    FEATURE_COLS,
    N_FEATURES,
    SEQ_LEN,
    FEATURE_MIN,
    FEATURE_MAX,
)


class TestWeatherLSTMArchitecture:
    def test_instantiation(self):
        model = WeatherLSTM()
        assert model is not None

    def test_forward_shape(self):
        model = WeatherLSTM()
        x = torch.randn(4, SEQ_LEN, N_FEATURES)
        out = model(x)
        assert out.shape == (4, 1), f"Expected (4,1) got {out.shape}"

    def test_n_features_matches_feature_cols(self):
        assert N_FEATURES == len(FEATURE_COLS)

    def test_single_sample_forward(self):
        model = WeatherLSTM()
        x = torch.randn(1, SEQ_LEN, N_FEATURES)
        out = model(x)
        assert out.shape == (1, 1)


class TestNormalisation:
    def test_normalise_min_gives_zero(self):
        arr = FEATURE_MIN.reshape(1, -1)
        norm = normalise(arr)
        assert np.allclose(norm, 0.0)

    def test_normalise_max_gives_one(self):
        arr = FEATURE_MAX.reshape(1, -1)
        norm = normalise(arr)
        assert np.allclose(norm, 1.0)

    def test_normalise_midpoint(self):
        mid = ((FEATURE_MIN + FEATURE_MAX) / 2).reshape(1, -1)
        norm = normalise(mid)
        assert np.allclose(norm, 0.5, atol=1e-5)

    def test_denormalise_temperature_zero(self):
        t = denormalise_temperature(0.0)
        assert t == pytest.approx(FEATURE_MIN[0])

    def test_denormalise_temperature_one(self):
        t = denormalise_temperature(1.0)
        assert t == pytest.approx(FEATURE_MAX[0])


class TestPredictNextTemperature:
    def _make_sequence(self):
        """Create a valid 24×6 sequence with mid-range values."""
        row = (FEATURE_MIN + FEATURE_MAX) / 2
        return np.tile(row, (SEQ_LEN, 1))

    def test_returns_dict(self):
        seq = self._make_sequence()
        result = predict_next_temperature(seq)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        seq = self._make_sequence()
        result = predict_next_temperature(seq)
        assert "predicted_temperature_celsius" in result
        assert "status" in result
        assert "message" in result

    def test_status_is_ok_or_untrained(self):
        seq = self._make_sequence()
        result = predict_next_temperature(seq)
        assert result["status"] in ("ok", "untrained", "error")

    def test_untrained_returns_none_prediction(self):
        """When weights are absent, prediction must be None (not fabricated)."""
        seq = self._make_sequence()
        result = predict_next_temperature(seq)
        if result["status"] == "untrained":
            assert result["predicted_temperature_celsius"] is None, (
                "LSTM must return None prediction when untrained — not fabricated values"
            )

    def test_ok_prediction_is_plausible_temperature(self):
        """When model is loaded, temperature must be in plausible range."""
        seq = self._make_sequence()
        result = predict_next_temperature(seq)
        if result["status"] == "ok":
            t = result["predicted_temperature_celsius"]
            assert -20 <= t <= 60, f"Implausible temperature: {t}"


class TestGetModelInfo:
    def test_returns_dict(self):
        info = get_model_info()
        assert isinstance(info, dict)

    def test_required_keys(self):
        info = get_model_info()
        for key in ("architecture", "layers", "hidden_size", "sequence_length",
                    "input_features", "output", "framework", "status"):
            assert key in info, f"Missing key: {key}"

    def test_architecture_is_lstm(self):
        info = get_model_info()
        assert "LSTM" in info["architecture"]

    def test_status_valid(self):
        info = get_model_info()
        assert info["status"] in ("ok", "untrained", "error")
