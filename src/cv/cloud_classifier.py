"""
Cloud / Weather Image Classifier — Computer Vision module.

Architecture
------------
A lightweight CNN built on top of a frozen MobileNetV2 backbone
(ImageNet pretrained, available from torchvision).

The head is a 5-class linear classifier:
  0  Clear
  1  Partly Cloudy
  2  Mostly Cloudy / Overcast
  3  Rain / Convective
  4  Thunderstorm / Severe

Status model
------------
The fine-tuned weights file ``best_cv_model.pt`` is NOT included in the
repository because a labelled satellite/cloud dataset is required for
fine-tuning (e.g. the EUMETSAT Cloud-Mask dataset or any cloud-image
dataset available from Kaggle/Zenodo).

When the weights file is absent the module:
  1. Uses the ImageNet backbone to extract a feature vector.
  2. Applies the untrained linear head → random/meaningless class scores.
  3. Returns status="untrained" and does NOT present those scores as real
     classifications.

This maintains architectural completeness while being truthful.

Usage
-----
    from src.cv.cloud_classifier import classify_image, get_cv_model_info

    # from a numpy array (H, W, 3) or file path
    result = classify_image(image_array)
    print(result)
"""
import os
import logging
from typing import Optional, Union

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLASS_NAMES = [
    "Clear",
    "Partly Cloudy",
    "Mostly Cloudy",
    "Rain / Convective",
    "Thunderstorm / Severe",
]
N_CLASSES = len(CLASS_NAMES)
IMG_SIZE = 224   # MobileNetV2 input

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "best_cv_model.pt",
)

# ImageNet normalisation
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

def _build_model() -> nn.Module:
    """Build MobileNetV2-based cloud classifier."""
    try:
        from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
        backbone = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
    except (ImportError, Exception):
        # Older torchvision
        try:
            from torchvision.models import mobilenet_v2
            backbone = mobilenet_v2(pretrained=True)
        except Exception as exc:
            logger.error("Could not load MobileNetV2: %s", exc)
            raise

    # Freeze backbone
    for param in backbone.features.parameters():
        param.requires_grad = False

    # Replace classifier head
    in_features = backbone.classifier[1].in_features
    backbone.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(in_features, N_CLASSES),
    )
    return backbone


# ---------------------------------------------------------------------------
# Lazy model state
# ---------------------------------------------------------------------------

_model: Optional[nn.Module] = None
_model_status: Optional[str] = None


def _load_model():
    global _model, _model_status

    if _model_status is not None:
        return _model, _model_status

    try:
        net = _build_model()
    except Exception as exc:
        _model_status = f"error: torchvision unavailable ({exc})"
        logger.error("CV model build failed: %s", exc)
        return None, _model_status

    if os.path.isfile(MODEL_PATH):
        try:
            state = torch.load(MODEL_PATH, map_location="cpu")
            net.load_state_dict(state)
            net.eval()
            _model = net
            _model_status = "ok"
            logger.info("CV model loaded from %s", MODEL_PATH)
        except Exception as exc:
            logger.error("CV model weight load failed: %s", exc)
            _model_status = f"error: {exc}"
            return None, _model_status
    else:
        # Return model with untrained head — backbone weights are ImageNet
        net.eval()
        _model = net
        _model_status = "untrained"
        logger.warning(
            "CV model weights not found at %s — "
            "backbone is ImageNet-pretrained but head is NOT fine-tuned. "
            "Do not trust class predictions.",
            MODEL_PATH,
        )

    return _model, _model_status


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(image: Union[np.ndarray, str]) -> Optional[torch.Tensor]:
    """
    Preprocess an image for the CNN.

    Args:
        image: numpy array (H, W, 3) uint8 OR a file path string.

    Returns:
        torch.Tensor of shape (1, 3, IMG_SIZE, IMG_SIZE) or None on error.
    """
    try:
        if isinstance(image, str):
            from PIL import Image as PILImage
            img = np.array(PILImage.open(image).convert("RGB"))
        elif isinstance(image, np.ndarray):
            img = image.astype(np.uint8)
        else:
            logger.error("preprocess_image: unsupported input type %s", type(image))
            return None

        # Resize
        from PIL import Image as PILImage
        pil = PILImage.fromarray(img).resize((IMG_SIZE, IMG_SIZE))
        arr = np.array(pil, dtype=np.float32) / 255.0

        # Normalise
        arr = (arr - _MEAN) / _STD

        # HWC → CHW → NCHW
        tensor = torch.tensor(arr).permute(2, 0, 1).unsqueeze(0)
        return tensor

    except Exception as exc:
        logger.error("Image preprocessing failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Public inference API
# ---------------------------------------------------------------------------

def classify_image(image: Union[np.ndarray, str, None]) -> dict:
    """
    Classify a weather/cloud image.

    Args:
        image: numpy (H, W, 3) uint8, file path, or None.

    Returns:
        dict:
          class_name         (str | None)
          class_index        (int | None)
          confidence         (float | None)   — only valid when status=="ok"
          all_probabilities  (dict | None)
          status             ("ok" | "untrained" | "unavailable" | "error")
          message            (str)
    """
    UNAVAILABLE = {
        "class_name": None,
        "class_index": None,
        "confidence": None,
        "all_probabilities": None,
    }

    if image is None:
        return {
            **UNAVAILABLE,
            "status": "unavailable",
            "message": "No image provided for classification.",
        }

    model, status = _load_model()

    if model is None:
        return {
            **UNAVAILABLE,
            "status": status,
            "message": f"CV model unavailable: {status}",
        }

    tensor = preprocess_image(image)
    if tensor is None:
        return {
            **UNAVAILABLE,
            "status": "error",
            "message": "Image preprocessing failed.",
        }

    try:
        with torch.no_grad():
            logits = model(tensor)          # (1, N_CLASSES)
            probs = torch.softmax(logits, dim=1).squeeze().numpy()

        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])

        prob_dict = {CLASS_NAMES[i]: round(float(probs[i]), 4) for i in range(N_CLASSES)}

        if status == "untrained":
            return {
                "class_name": None,
                "class_index": None,
                "confidence": None,
                "all_probabilities": None,
                "status": "untrained",
                "message": (
                    "CV classifier backbone is ImageNet-pretrained but the "
                    "cloud-classification head has NOT been fine-tuned. "
                    "Predictions are not meaningful. "
                    "Fine-tune with a labelled cloud dataset and save weights "
                    f"to {MODEL_PATH}."
                ),
            }

        return {
            "class_name": CLASS_NAMES[top_idx],
            "class_index": top_idx,
            "confidence": round(top_conf, 4),
            "all_probabilities": prob_dict,
            "status": "ok",
            "message": "Classification successful.",
        }

    except Exception as exc:
        logger.error("CV inference failed: %s", exc)
        return {
            **UNAVAILABLE,
            "status": "error",
            "message": f"CV inference error: {exc}",
        }


def get_cv_model_info() -> dict:
    """Return metadata about the CV model."""
    _, status = _load_model()
    return {
        "architecture": "MobileNetV2 + Linear Head",
        "backbone": "MobileNetV2 (ImageNet pretrained)",
        "classes": CLASS_NAMES,
        "n_classes": N_CLASSES,
        "input_size": f"{IMG_SIZE}x{IMG_SIZE}",
        "framework": "PyTorch + torchvision",
        "model_path": MODEL_PATH,
        "status": status,
        "training_note": (
            "Fine-tune on a labelled cloud/satellite image dataset "
            "(e.g. EUMETSAT, Kaggle cloud datasets) and save weights "
            f"to {MODEL_PATH}."
        ),
    }
