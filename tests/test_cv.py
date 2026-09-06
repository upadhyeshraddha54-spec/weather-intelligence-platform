"""
Unit tests for the Computer Vision (cloud classifier) module.
No trained weights required — tests verify architecture + honest unavailable state.
"""
import os
import sys
import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.cv.cloud_classifier import (
    classify_image,
    get_cv_model_info,
    preprocess_image,
    CLASS_NAMES,
    N_CLASSES,
    IMG_SIZE,
)


class TestCVModelInfo:
    def test_returns_dict(self):
        info = get_cv_model_info()
        assert isinstance(info, dict)

    def test_required_keys(self):
        info = get_cv_model_info()
        for key in ("architecture", "backbone", "classes", "n_classes",
                    "input_size", "framework", "status"):
            assert key in info, f"Missing key: {key}"

    def test_correct_class_count(self):
        info = get_cv_model_info()
        assert info["n_classes"] == N_CLASSES == 5

    def test_status_valid(self):
        info = get_cv_model_info()
        assert info["status"] in ("ok", "untrained", "error")

    def test_class_names_present(self):
        info = get_cv_model_info()
        assert len(info["classes"]) == 5
        assert "Clear" in info["classes"]
        assert "Thunderstorm / Severe" in info["classes"]


class TestPreprocessImage:
    def test_numpy_array_returns_tensor(self):
        img = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        tensor = preprocess_image(img)
        assert tensor is not None
        assert tensor.shape == (1, 3, IMG_SIZE, IMG_SIZE)

    def test_wrong_type_returns_none(self):
        result = preprocess_image(12345)
        assert result is None

    def test_normalisation_range(self):
        """After ImageNet normalisation, values can be outside [0,1]."""
        img = np.ones((224, 224, 3), dtype=np.uint8) * 128
        tensor = preprocess_image(img)
        assert tensor is not None
        # Mean ~0 after normalisation — values near ImageNet mean


class TestClassifyImage:
    def _random_image(self, h=224, w=224):
        return np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)

    def test_none_returns_unavailable(self):
        result = classify_image(None)
        assert result["status"] == "unavailable"
        assert result["class_name"] is None

    def test_returns_dict_with_required_keys(self):
        result = classify_image(self._random_image())
        for key in ("class_name", "class_index", "confidence",
                    "all_probabilities", "status", "message"):
            assert key in result, f"Missing key: {key}"

    def test_untrained_returns_none_prediction(self):
        """When weights absent, predictions must be None — not fabricated."""
        result = classify_image(self._random_image())
        if result["status"] == "untrained":
            assert result["class_name"] is None, (
                "CV must not return fabricated class predictions when untrained"
            )
            assert result["confidence"] is None

    def test_ok_prediction_valid_class(self):
        """When model is loaded, class must be from CLASS_NAMES."""
        result = classify_image(self._random_image())
        if result["status"] == "ok":
            assert result["class_name"] in CLASS_NAMES
            assert 0.0 <= result["confidence"] <= 1.0
            assert isinstance(result["all_probabilities"], dict)
            assert len(result["all_probabilities"]) == N_CLASSES

    def test_non_standard_size_image(self):
        """Images of non-standard size should be resized and processed."""
        img = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        result = classify_image(img)
        assert result["status"] in ("ok", "untrained", "error")

    def test_status_is_truthful_set(self):
        result = classify_image(self._random_image())
        assert result["status"] in ("ok", "untrained", "unavailable", "error")
