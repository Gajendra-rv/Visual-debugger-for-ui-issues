"""
Training script for CNN UI Bug Detector.
Uses MobileNetV2 backbone (frozen) + custom Dense head.

Usage:
    python -m app.ml.train --data ml_experiments/data/processed --epochs 30
"""
import os
import argparse
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
)
import sqlite3
from datetime import datetime

IMG_SIZE    = (224, 224)
N_CLASSES   = 6   # layout, color, overlap, missing, alignment, contrast
BATCH_SIZE  = 32
EPOCHS      = 30
LR          = 1e-4
DB_PATH     = "instance/debugger.db"


def build_model(n_classes: int = N_CLASSES) -> keras.Model:
    """MobileNetV2 + custom classification head."""
    base = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    # Freeze base layers
    for layer in base.layers[:-20]:
        layer.trainable = False

    inputs  = keras.Input(shape=(*IMG_SIZE, 3))
    x       = base(inputs, training=False)
    x       = layers.GlobalAveragePooling2D()(x)
    x       = layers.Dense(512, activation="relu")(x)
    x       = layers.Dropout(0.4)(x)
    x       = layers.Dense(256, activation="relu")(x)
    x       = layers.Dropout(0.3)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)  # multi-class classification

    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(LR),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")]
    )
    return model


class MetricsLogger(keras.callbacks.Callback):
    """Logs epoch metrics to the SQLite database."""
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO model_metrics (epoch, train_acc, val_acc, train_loss, val_loss)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    epoch + 1,
                    float(logs.get('accuracy', 0)),
                    float(logs.get('val_accuracy', 0)),
                    float(logs.get('loss', 0)),
                    float(logs.get('val_loss', 0))
                )
            )
            conn.commit()
            conn.close()
            print(f" - Logged metrics to DB for epoch {epoch+1}")
        except Exception as e:
            print(f" - Error logging metrics to DB: {e}")


def load_dataset(data_dir: str):
    """Load images from data_dir using ImageDataGenerator."""
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    datagen_train = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=5,
        width_shift_range=0.05,
        height_shift_range=0.05,
        brightness_range=[0.85, 1.15],
        horizontal_flip=False,
        validation_split=0.2,
    )
    datagen_val = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    train_gen = datagen_train.flow_from_directory(
        os.path.join(data_dir, "train"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        shuffle=True,
    )
    val_gen = datagen_val.flow_from_directory(
        os.path.join(data_dir, "train"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )
    return train_gen, val_gen


def train(data_dir: str, model_out: str, epochs: int = EPOCHS):
    print("Loading dataset…")
    train_gen, val_gen = load_dataset(data_dir)

    print("Building model…")
    model = build_model(n_classes=train_gen.num_classes)
    model.summary()

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        ModelCheckpoint(model_out, save_best_only=True, monitor="val_accuracy", verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7, verbose=1),
        TensorBoard(log_dir="logs/tensorboard", histogram_freq=1),
        MetricsLogger(DB_PATH)
    ]

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks,
    )

    print(f"\n✓ Model saved to {model_out}")
    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CNN UI Bug Detector")
    parser.add_argument("--data",   default="dataset", help="Data directory")
    parser.add_argument("--output", default="app/static/models/ui_bug_detector.keras", help="Output model path")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of epochs")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    train(args.data, args.output, args.epochs)
