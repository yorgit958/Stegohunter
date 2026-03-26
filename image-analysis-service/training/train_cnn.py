"""
StegoHunter CNN Training Script
================================
Run this on Kaggle or Google Colab (free GPU).

Dataset: https://www.kaggle.com/datasets/marcozuppelli/stego-images-dataset
Model: https://www.kaggle.com/code/zobayer0x01/steganography-detector (reference)

Usage on Kaggle:
1. Create a new notebook on Kaggle
2. Add the "Stego Images Dataset" by marcozuppelli
3. Paste this entire script into a cell and run
4. Download the generated `cnn_steg_detector.h5` file
5. Place it in: image-analysis-service/ml_models/cnn_steg_detector.h5

Usage on Google Colab:
1. Upload this script or paste into a cell
2. Download the dataset manually or mount Kaggle API
3. Adjust DATA_DIR below
4. Run and download the .h5 file
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# ============================
# Configuration
# ============================
# Kaggle dataset path (default Kaggle notebook path)
DATA_DIR = "/kaggle/input/stego-images-dataset"
# Colab alternative: DATA_DIR = "/content/stego-images-dataset"

OUTPUT_MODEL_PATH = "cnn_steg_detector.h5"
IMG_SIZE = 128  # 128x128x3 as per architecture spec
BATCH_SIZE = 32
EPOCHS = 100
VALIDATION_SPLIT = 0.2
EARLY_STOPPING_PATIENCE = 10

# ============================
# 1. Load and Preprocess Data
# ============================
print("=" * 60)
print("StegoHunter CNN Training Pipeline")
print("=" * 60)


def load_dataset(data_dir, img_size):
    """
    Load the Stego-Images-Dataset.
    Expected structure:
      data_dir/
        clean/   (or cover/ or original/)
          *.png
        stego/   (or embedded/ or steg/)
          *.png
    """
    import cv2
    from pathlib import Path

    images = []
    labels = []

    # Auto-detect folder names
    data_path = Path(data_dir)
    subdirs = [d.name.lower() for d in data_path.iterdir() if d.is_dir()]
    print(f"Found subdirectories: {subdirs}")

    # Map folder names to labels
    clean_names = {"clean", "cover", "original", "covers", "originals", "non_stego", "normal"}
    stego_names = {"stego", "embedded", "steg", "stegos", "steganographic", "malicious"}

    clean_dir = None
    stego_dir = None

    for d in data_path.iterdir():
        if d.is_dir():
            name = d.name.lower()
            if name in clean_names:
                clean_dir = d
            elif name in stego_names:
                stego_dir = d

    if clean_dir is None or stego_dir is None:
        # Fallback: assume first two directories
        dirs = sorted([d for d in data_path.iterdir() if d.is_dir()])
        if len(dirs) >= 2:
            clean_dir, stego_dir = dirs[0], dirs[1]
            print(f"Auto-assigned: '{clean_dir.name}' = clean, '{stego_dir.name}' = stego")
        else:
            raise FileNotFoundError(
                f"Could not find clean/stego subdirectories in {data_dir}. "
                f"Found: {subdirs}"
            )

    print(f"\nLoading clean images from: {clean_dir}")
    print(f"Loading stego images from: {stego_dir}")

    # Load clean images (label = 0)
    clean_files = list(clean_dir.glob("*.png")) + list(clean_dir.glob("*.jpg"))
    print(f"  Clean files found: {len(clean_files)}")

    for img_path in clean_files:
        img = cv2.imread(str(img_path))
        if img is not None:
            img = cv2.resize(img, (img_size, img_size))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            labels.append(0)

    # Load stego images (label = 1)
    stego_files = list(stego_dir.glob("*.png")) + list(stego_dir.glob("*.jpg"))
    print(f"  Stego files found: {len(stego_files)}")

    for img_path in stego_files:
        img = cv2.imread(str(img_path))
        if img is not None:
            img = cv2.resize(img, (img_size, img_size))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            labels.append(1)

    images = np.array(images, dtype=np.float32) / 255.0  # Normalize to [0, 1]
    labels = np.array(labels, dtype=np.float32)

    print(f"\nTotal images loaded: {len(images)}")
    print(f"  Clean: {np.sum(labels == 0):.0f}")
    print(f"  Stego: {np.sum(labels == 1):.0f}")

    return images, labels


# Load the dataset
X, y = load_dataset(DATA_DIR, IMG_SIZE)

# Split into train/validation
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=VALIDATION_SPLIT, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train)} images")
print(f"Validation set: {len(X_val)} images")

# ============================
# 2. Build the CNN Model
# ============================
print("\n" + "=" * 60)
print("Building CNN Model (8.7M parameters)")
print("=" * 60)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, BatchNormalization,
    Dropout, Flatten, Dense, Input,
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint,
)
from tensorflow.keras.optimizers import Adam

model = Sequential([
    Input(shape=(IMG_SIZE, IMG_SIZE, 3)),

    # Block 1: 32 filters
    Conv2D(32, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),

    # Block 2: 64 filters
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),

    # Block 3: 128 filters
    Conv2D(128, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(128, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),

    # Dense classification head
    Flatten(),
    Dense(512, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(1, activation='sigmoid'),
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy'],
)

model.summary()
print(f"\nTotal parameters: {model.count_params():,}")

# ============================
# 3. Train the Model
# ============================
print("\n" + "=" * 60)
print(f"Training for {EPOCHS} epochs (batch size {BATCH_SIZE})")
print("=" * 60)

callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=EARLY_STOPPING_PATIENCE,
        restore_best_weights=True,
        verbose=1,
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1,
    ),
    ModelCheckpoint(
        OUTPUT_MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        save_weights_only=True,
        verbose=1,
    ),
]

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1,
)

# ============================
# 4. Evaluate
# ============================
print("\n" + "=" * 60)
print("Evaluation Results")
print("=" * 60)

# Load best weights
model.load_weights(OUTPUT_MODEL_PATH)

y_pred_proba = model.predict(X_val, verbose=0).flatten()
y_pred = (y_pred_proba > 0.5).astype(int)

print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=["Clean", "Stego"]))

print(f"ROC-AUC Score: {roc_auc_score(y_val, y_pred_proba):.4f}")

cm = confusion_matrix(y_val, y_pred)
print(f"\nConfusion Matrix:")
print(f"  True Negatives:  {cm[0][0]}")
print(f"  False Positives: {cm[0][1]}")
print(f"  False Negatives: {cm[1][0]}")
print(f"  True Positives:  {cm[1][1]}")

# ============================
# 5. Plot Training History
# ============================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history.history['accuracy'], label='Train Accuracy')
ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
ax1.set_title('Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(history.history['loss'], label='Train Loss')
ax2.plot(history.history['val_loss'], label='Val Loss')
ax2.set_title('Model Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_history.png', dpi=150)
plt.show()

# ============================
# 6. Save Final Model
# ============================
print(f"\n{'=' * 60}")
print(f"Model saved to: {OUTPUT_MODEL_PATH}")
print(f"File size: {os.path.getsize(OUTPUT_MODEL_PATH) / (1024*1024):.1f} MB")
print(f"{'=' * 60}")
print(f"\nNext steps:")
print(f"1. Download '{OUTPUT_MODEL_PATH}' from this notebook")
print(f"2. Place it in: image-analysis-service/ml_models/cnn_steg_detector.h5")
print(f"3. Restart the Image Analysis Service — CNN will auto-load!")
