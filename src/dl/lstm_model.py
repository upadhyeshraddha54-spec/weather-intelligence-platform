"""
LSTM-based weather time-series forecasting model.

Architecture
------------
A two-layer stacked LSTM followed by a linear output head.
The model takes a sequence of historical weather observations
and predicts the next-step temperature (regression).

Training
--------
The model is NOT pre-trained; a ``best_dl_model.pt`` weights
file is required for inference.  When the weights file is absent
the module returns an honest ``UNTRAINED`` status rather than
fabricating predictions.

Use ``train_lstm()`` to train on the provided ``weather_data.csv``.

Data contract
-------------
Input features (in order):
  0  temperature     (°C)
  1  humidity        (%)
  2  precipitation   (mm)
  3  wind_speed      (km/h)
  4  month           (1–12)
  5  hour            (0–23)

Target:
  temperature at next time step (°C)
"""
import os
import logging
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    "temperature",
    "humidity",
    "precipitation",
    "wind_speed",
    "month",
    "hour",
]
N_FEATURES = len(FEATURE_COLS)
SEQ_LEN = 24          # 24 time steps (e.g. 24 hours) used as look-back
HIDDEN_SIZE = 64
NUM_LAYERS = 2
OUTPUT_SIZE = 1

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "best_dl_model.pt",
)


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

class WeatherLSTM(nn.Module):
    """Stacked LSTM for weather temperature prediction."""

    def __init__(
        self,
        n_features: int = N_FEATURES,
        hidden_size: int = HIDDEN_SIZE,
        num_layers: int = NUM_LAYERS,
        output_size: int = OUTPUT_SIZE,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, n_features)

        Returns:
            (batch, output_size)
        """
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
        out, _ = self.lstm(x, (h0, c0))
        # Use the last time-step output
        return self.fc(out[:, -1, :])


# ---------------------------------------------------------------------------
# Normalisation helpers (min-max, stored as module-level constants)
# ---------------------------------------------------------------------------
# These defaults are derived from representative Indian climate ranges.
# When training on real data, pass actual min/max arrays to the training
# function which will persist them alongside the model weights.

FEATURE_MIN = np.array([10.0,  5.0, 0.0,  0.0, 1.0,  0.0], dtype=np.float32)
FEATURE_MAX = np.array([45.0, 100.0, 200.0, 120.0, 12.0, 23.0], dtype=np.float32)


def normalise(x: np.ndarray) -> np.ndarray:
    """Min-max normalise features to [0, 1]."""
    denom = FEATURE_MAX - FEATURE_MIN
    denom[denom == 0] = 1.0
    return (x - FEATURE_MIN) / denom


def denormalise_temperature(t: float) -> float:
    """Convert normalised temperature back to °C."""
    return float(t) * (FEATURE_MAX[0] - FEATURE_MIN[0]) + FEATURE_MIN[0]


# ---------------------------------------------------------------------------
# Lazy model loading
# ---------------------------------------------------------------------------

_model: Optional[WeatherLSTM] = None
_model_status: Optional[str] = None   # "ok" | "untrained" | "error"


def _load_model() -> Tuple[Optional[WeatherLSTM], str]:
    global _model, _model_status

    if _model_status is not None:
        return _model, _model_status

    if not os.path.isfile(MODEL_PATH):
        logger.warning(
            "DL model weights not found at %s. "
            "Run src/dl/train.py to train the model.",
            MODEL_PATH,
        )
        _model_status = "untrained"
        return None, "untrained"

    try:
        net = WeatherLSTM()
        net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        net.eval()
        _model = net
        _model_status = "ok"
        logger.info("DL model loaded from %s", MODEL_PATH)
        return net, "ok"
    except Exception as exc:
        logger.error("DL model failed to load: %s", exc)
        _model_status = "error"
        return None, f"error: {exc}"


# ---------------------------------------------------------------------------
# Public inference API
# ---------------------------------------------------------------------------

def predict_next_temperature(sequence: np.ndarray) -> dict:
    """
    Predict the next time-step temperature from a historical sequence.

    Args:
        sequence: numpy array of shape (SEQ_LEN, N_FEATURES) with
                  columns in FEATURE_COLS order.

    Returns:
        dict with keys:
          predicted_temperature_celsius  (float | None)
          status                         ("ok" | "untrained" | "error")
          message                        (str)
    """
    model, status = _load_model()

    if model is None:
        return {
            "predicted_temperature_celsius": None,
            "status": status,
            "message": (
                "LSTM model is not trained. "
                "Run `python src/dl/train.py` to train on weather_data.csv."
                if status == "untrained"
                else f"LSTM model could not be loaded: {status}"
            ),
        }

    try:
        seq = sequence.astype(np.float32)
        seq_norm = normalise(seq)
        tensor = torch.tensor(seq_norm[np.newaxis, :, :])  # (1, seq, feat)

        with torch.no_grad():
            pred = model(tensor)            # (1, 1)
            temp = pred.item()

        # Only denorm if the output appears normalised (within [0,1])
        if 0.0 <= temp <= 1.0:
            temp = denormalise_temperature(temp)

        return {
            "predicted_temperature_celsius": round(temp, 2),
            "status": "ok",
            "message": "LSTM prediction successful.",
        }
    except Exception as exc:
        logger.error("LSTM inference failed: %s", exc)
        return {
            "predicted_temperature_celsius": None,
            "status": "error",
            "message": f"LSTM inference error: {exc}",
        }


def get_model_info() -> dict:
    """Return metadata about the LSTM model."""
    _, status = _load_model()
    return {
        "architecture": "Stacked LSTM",
        "layers": NUM_LAYERS,
        "hidden_size": HIDDEN_SIZE,
        "sequence_length": SEQ_LEN,
        "input_features": FEATURE_COLS,
        "output": "next-step temperature (°C)",
        "framework": "PyTorch",
        "model_path": MODEL_PATH,
        "status": status,
    }
