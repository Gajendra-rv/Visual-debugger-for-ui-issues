"""Model evaluation script — accuracy, F1, confusion matrix."""
import os, json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)

BUG_CLASSES = ["layout", "color", "overlap", "missing", "alignment", "contrast"]


def evaluate_model(model_path: str, data_dir: str, output_dir: str = "ml_experiments"):
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    model = tf.keras.models.load_model(model_path)
    datagen = ImageDataGenerator(rescale=1.0 / 255)
    test_gen = datagen.flow_from_directory(
        os.path.join(data_dir, "test"),
        target_size=(224, 224),
        batch_size=32,
        class_mode="categorical",
        shuffle=False,
    )

    preds = model.predict(test_gen)
    y_pred = np.argmax(preds, axis=1)
    y_true = test_gen.classes
    labels = list(test_gen.class_indices.keys())

    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_true, y_pred,    average="weighted", zero_division=0)
    f1   = f1_score(y_true, y_pred,        average="weighted", zero_division=0)

    report = classification_report(y_true, y_pred, target_names=labels)
    print(report)
    print(f"Accuracy: {acc:.4f}  Precision: {prec:.4f}  Recall: {rec:.4f}  F1: {f1:.4f}")

    metrics = {"accuracy": acc, "precision": prec, "recall": rec, "f1_score": f1}
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_title("Confusion Matrix — CNN UI Bug Detector")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"), dpi=150)
    print(f"✓ Saved confusion matrix to {output_dir}/confusion_matrix.png")

    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="app/static/models/ui_bug_detector.keras")
    parser.add_argument("--data",  default="ml_experiments/data/processed")
    parser.add_argument("--out",   default="ml_experiments")
    args = parser.parse_args()
    evaluate_model(args.model, args.data, args.out)
