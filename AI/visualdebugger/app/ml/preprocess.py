"""Image preprocessing pipeline for the CNN model."""
import numpy as np
from PIL import Image
import cv2


IMG_SIZE = (224, 224)


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Full preprocessing pipeline:
    1. Load image
    2. Resize to 224x224
    3. Apply CLAHE for contrast enhancement
    4. Normalize to [0, 1]
    5. Add batch dimension → shape (1, 224, 224, 3)
    """
    # Load
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)

    # CLAHE on LAB channels
    lab = cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    # Normalize
    normalized = enhanced.astype(np.float32) / 255.0

    # MobileNetV2 preprocessing expects [-1, 1]
    mobilenet_input = (normalized - 0.5) * 2.0

    return np.expand_dims(mobilenet_input, axis=0)


def preprocess_pil(pil_image: Image.Image) -> np.ndarray:
    """Preprocess a PIL Image directly (no file load needed)."""
    img = pil_image.convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    normalized = img_array / 255.0
    mobilenet_input = (normalized - 0.5) * 2.0
    return np.expand_dims(mobilenet_input, axis=0)


def extract_regions(image_path: str, n_regions: int = 4) -> list:
    """
    Split the screenshot into N vertical strips for regional analysis.
    Returns list of (region_array, bbox) tuples.
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    regions = []
    strip_h = h // n_regions
    for i in range(n_regions):
        y0 = i * strip_h
        y1 = (i + 1) * strip_h if i < n_regions - 1 else h
        region = img.crop((0, y0, w, y1))
        arr = preprocess_pil(region)
        bbox = {"x": 0, "y": y0, "w": w, "h": y1 - y0}
        regions.append((arr, bbox))
    return regions
