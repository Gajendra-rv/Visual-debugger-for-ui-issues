"""
Convert YOLO object detection dataset to Keras Image Classification format.
It reads the YOLO labels, crops the bounding boxes, and saves them 
into folders based on their class names.
"""
import os
import yaml
import glob
from PIL import Image

def convert_yolo_to_keras(yolo_dir, output_dir):
    yaml_path = os.path.join(yolo_dir, "dataset.yaml")
    if not os.path.exists(yaml_path):
        print(f"❌ Error: dataset.yaml not found in {yolo_dir}")
        return

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # YOLO v8/v5 yaml format can be a list or dict for names
    if isinstance(data.get('names'), dict):
        classes = data['names']
    elif isinstance(data.get('names'), list):
        classes = {i: name for i, name in enumerate(data['names'])}
    else:
        print("❌ Error: Could not parse class names from dataset.yaml")
        return

    print(f"Found classes: {classes}")

    # Create output directories
    train_out = os.path.join(output_dir, "train")
    for cls_name in classes.values():
        os.makedirs(os.path.join(train_out, cls_name), exist_ok=True)

    # Process images in train directory
    train_images_dir = os.path.join(yolo_dir, "train", "images")
    train_labels_dir = os.path.join(yolo_dir, "train", "labels")

    if not os.path.exists(train_images_dir):
        # Sometimes images are just directly inside train/
        train_images_dir = os.path.join(yolo_dir, "train")
        train_labels_dir = os.path.join(yolo_dir, "train")

    image_paths = glob.glob(os.path.join(train_images_dir, "*.*"))
    valid_exts = {".jpg", ".jpeg", ".png"}
    image_paths = [p for p in image_paths if os.path.splitext(p)[1].lower() in valid_exts]

    print(f"Found {len(image_paths)} images to process...")
    crops_saved = 0

    for img_path in image_paths:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        label_path = os.path.join(train_labels_dir, f"{base_name}.txt")

        if not os.path.exists(label_path):
            continue

        try:
            img = Image.open(img_path).convert("RGB")
            W, H = img.size
        except Exception as e:
            print(f"Skipping {img_path}: {e}")
            continue

        with open(label_path, "r") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            
            cls_id = int(parts[0])
            if cls_id not in classes:
                continue

            # YOLO format: class_id center_x center_y width height (normalized 0-1)
            cx, cy, w, h = map(float, parts[1:5])
            
            # Convert to absolute pixel coordinates
            px_w = w * W
            px_h = h * H
            if px_w <= 0 or px_h <= 0:
                continue
            px_x = (cx * W) - (px_w / 2)
            px_y = (cy * H) - (px_h / 2)

            # Crop the bounding box
            crop = img.crop((px_x, px_y, px_x + px_w, px_y + px_h))
            
            if crop.size[0] == 0 or crop.size[1] == 0:
                continue
            
            cls_name = classes[cls_id]
            save_path = os.path.join(train_out, cls_name, f"{base_name}_crop_{idx}.jpg")
            crop.save(save_path)
            crops_saved += 1

    print(f"\n✅ Success! Created {crops_saved} cropped images for Keras classification.")
    print(f"Your Keras-ready dataset is now located at: {train_out}")
    print("\nYou can now train your model using:")
    print(f"python app/ml/train.py --data \"{output_dir}\" --epochs 30")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("YOLO to Keras Classification Converter")
    parser.add_argument("--yolo_dir", required=True, help="Path to the downloaded YOLO dataset folder")
    parser.add_argument("--output_dir", default="ml_experiments/data/processed", help="Path to save the Keras dataset")
    args = parser.parse_args()
    
    convert_yolo_to_keras(args.yolo_dir, args.output_dir)
