"""
CNN Model Loader & Inference Engine
Uses MobileNetV2 (transfer learning) with a custom classification head.
Falls back to a lightweight mock model if no .h5 file is present.
"""
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

_model = None  # Singleton


def load_model(model_path: str):
    """Load and cache the Keras model."""
    global _model
    if _model is not None:
        return _model

    if not os.path.exists(model_path):
        logger.warning("Model file not found at %s — using mock predictions.", model_path)
        _model = _MockModel()
        return _model

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(model_path)
        logger.info("CNN model loaded from %s", model_path)
    except Exception as e:
        logger.error("Failed to load model: %s — using mock.", e)
        _model = _MockModel()
    return _model


def predict_bugs(image_array: np.ndarray, model) -> list[dict]:
    """
    Run model inference on a preprocessed image array.

    Returns a list of prediction dicts:
    [{ bug_type, confidence, severity, description }]
    """
    BUG_CLASSES = [
        "button", "checkbox", "clickable", "dropdown", "icon", "image", 
        "input", "label", "link", "menu_item", "radio", "select", 
        "slider", "text", "textarea", "toggle"
    ]
    SEVERITY_MAP = {
        "button": "low", "checkbox": "low", "clickable": "low", 
        "dropdown": "medium", "icon": "low", "image": "low", 
        "input": "medium", "label": "low", "link": "low", 
        "menu_item": "medium", "radio": "low", "select": "medium", 
        "slider": "medium", "text": "low", "textarea": "medium", "toggle": "medium"
    }
    DESCRIPTIONS = {
        "button":    "Interactive button element detected.",
        "checkbox":  "Checkbox selection element detected.",
        "clickable": "Generic clickable element or touch target detected.",
        "dropdown":  "Dropdown or select menu component detected.",
        "icon":      "Symbolic icon or glyph detected.",
        "image":     "Visual image or illustration asset detected.",
        "input":     "Text input field detected.",
        "label":     "Textual label associated with a UI element.",
        "link":      "Hyperlink or navigation anchor detected.",
        "menu_item": "Individual item within a navigation or context menu.",
        "radio":     "Radio button for mutually exclusive selection.",
        "select":    "Selectable list or menu component.",
        "slider":    "Range selection element or slider control.",
        "text":      "Static text content block detected.",
        "textarea":  "Multi-line text input area detected.",
        "toggle":    "On/off switch or toggle component detected.",
    }

    probs = model.predict(image_array)  # shape (1, 6) or similar

    if hasattr(probs, "numpy"):
        probs = probs.numpy()
    probs = np.array(probs).flatten()

    bugs = []
    threshold = 0.40
    for i, prob in enumerate(probs[:len(BUG_CLASSES)]):
        if float(prob) >= threshold:
            btype = BUG_CLASSES[i]
            bugs.append({
                "bug_type":    btype,
                "confidence":  round(float(prob), 4),
                "severity":    SEVERITY_MAP[btype],
                "description": DESCRIPTIONS[btype],
            })

    bugs.sort(key=lambda x: x["confidence"], reverse=True)
    return bugs


class _MockModel:
    """Lightweight mock model for demo / fallback when no .h5 is available."""

    def predict(self, image_array):
        import random
        np.random.seed(42)
        # Return realistic-looking probabilities
        probs = np.array([[
            round(random.uniform(0.30, 0.92), 4),  # layout
            round(random.uniform(0.20, 0.75), 4),  # color
            round(random.uniform(0.10, 0.65), 4),  # overlap
            round(random.uniform(0.05, 0.50), 4),  # missing
            round(random.uniform(0.25, 0.80), 4),  # alignment
            round(random.uniform(0.15, 0.70), 4),  # contrast
        ]])
        return probs
