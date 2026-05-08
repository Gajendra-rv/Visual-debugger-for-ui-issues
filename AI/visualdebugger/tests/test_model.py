"""Test suite for ML model and preprocessing."""
import os, sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_preprocess_returns_correct_shape(tmp_path):
    from PIL import Image
    from app.ml.preprocess import preprocess_image
    img = Image.new("RGB", (800, 600), color=(100, 150, 200))
    p = str(tmp_path / "test.png")
    img.save(p)
    arr = preprocess_image(p)
    assert arr.shape == (1, 224, 224, 3)
    assert arr.dtype == np.float32


def test_preprocess_normalized(tmp_path):
    from PIL import Image
    from app.ml.preprocess import preprocess_image
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    p = str(tmp_path / "white.png")
    img.save(p)
    arr = preprocess_image(p)
    assert arr.max() <= 1.05  # allow tiny float error


def test_mock_model_predict():
    from app.ml.model import _MockModel, predict_bugs
    import numpy as np
    model = _MockModel()
    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    bugs = predict_bugs(dummy, model)
    assert isinstance(bugs, list)
    for b in bugs:
        assert "bug_type" in b
        assert "confidence" in b
        assert 0.0 <= b["confidence"] <= 1.0


def test_extract_regions(tmp_path):
    from PIL import Image
    from app.ml.preprocess import extract_regions
    img = Image.new("RGB", (1280, 720), color=(50, 60, 70))
    p = str(tmp_path / "page.png")
    img.save(p)
    regions = extract_regions(p, n_regions=4)
    assert len(regions) == 4
    for arr, bbox in regions:
        assert arr.shape == (1, 224, 224, 3)
        assert "x" in bbox and "y" in bbox
