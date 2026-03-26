"""
CNN Classifier for steganography detection.  # v2: Kaggle model support

Supports two loading modes:
1. Full model file from Kaggle (steganalysis_cnn_model.h5) — loaded via load_model()
2. Weights-only file trained with our script (cnn_steg_detector.h5) — loaded via load_weights()

If neither file exists or TensorFlow is unavailable, the classifier signals
that it's unavailable and the ensemble works with statistical engines only.
"""

import os
import numpy as np
from typing import Optional
from app.engines.base import EngineResult

# Path to the model files (3 levels up: classifiers -> app -> image-analysis-service)
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_models")

# Supported model files (checked in order)
MODEL_FILES = [
    ("steganalysis_cnn_model.h5", "full_model"),     # Kaggle notebook output (model.save())
    ("cnn_steg_detector.h5", "weights_only"),         # Our training script output (save_weights())
]

# Lazy-loaded model reference
_model = None
_model_loaded = False
_model_available = False


def _build_model_for_weights():
    """
    Build a CNN architecture for loading weights from our training script.
    Must match the architecture in training/train_cnn.py exactly.
    """
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import (
            Conv2D, MaxPooling2D, BatchNormalization,
            Dropout, Flatten, Dense, Input,
        )

        model = Sequential([
            Input(shape=(128, 128, 3)),

            # Block 1
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Dropout(0.25),

            # Block 2
            Conv2D(64, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            Conv2D(64, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Dropout(0.25),

            # Block 3
            Conv2D(128, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            Conv2D(128, (3, 3), activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Dropout(0.25),

            # Dense head
            Flatten(),
            Dense(512, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(1, activation='sigmoid'),
        ])

        return model

    except ImportError:
        return None


def _load_model():
    """Attempt to load the CNN model from available files."""
    global _model, _model_loaded, _model_available

    if _model_loaded:
        return

    _model_loaded = True

    # Check for TensorFlow availability
    try:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF warnings before import
        import tensorflow as tf
    except Exception as e:
        print(f"[CNN] TensorFlow unavailable ({type(e).__name__}: {e}). CNN classifier disabled.")
        _model_available = False
        return

    # Try each model file in order
    for filename, load_type in MODEL_FILES:
        filepath = os.path.join(MODEL_DIR, filename)

        if not os.path.exists(filepath):
            continue

        if os.path.getsize(filepath) < 1000:
            print(f"[CNN] {filename} is too small (likely a placeholder). Skipping.")
            continue

        try:
            if load_type == "full_model":
                # Kaggle model: saved with model.save() — contains architecture + weights
                _model = tf.keras.models.load_model(filepath, compile=False)
                _model_available = True
                print(f"[CNN] Loaded FULL model from {filename} ({_model.count_params():,} parameters)")
                return

            elif load_type == "weights_only":
                # Our training script: saved with save_weights() — needs architecture rebuild
                model = _build_model_for_weights()
                if model is None:
                    continue
                model.load_weights(filepath)
                _model = model
                _model_available = True
                print(f"[CNN] Loaded WEIGHTS from {filename} ({_model.count_params():,} parameters)")
                return

        except Exception as e:
            print(f"[CNN] Failed to load {filename}: {e}")
            continue

    print(f"[CNN] No valid model file found in {MODEL_DIR}")
    print(f"[CNN] Expected one of: {[f[0] for f in MODEL_FILES]}")
    print("[CNN] CNN classifier will be disabled. Download or train a model first.")
    _model_available = False


def is_cnn_available() -> bool:
    """Check if the CNN model is loaded and ready."""
    _load_model()
    return _model_available


def predict(image: np.ndarray) -> Optional[EngineResult]:
    """
    Run CNN inference on a single image.

    Args:
        image: NumPy array (H, W, C) in uint8 BGR format.

    Returns:
        EngineResult with the CNN prediction, or None if model is unavailable.
    """
    _load_model()

    if not _model_available or _model is None:
        return None

    try:
        import cv2

        # Preprocess: resize to 128x128, convert BGR→RGB, normalize to [0, 1]
        resized = cv2.resize(image, (128, 128), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0

        # Add batch dimension: (1, 128, 128, 3)
        batch = np.expand_dims(normalized, axis=0)

        # Predict
        prediction = float(_model.predict(batch, verbose=0)[0][0])

        return EngineResult(
            engine_name="CNN Classifier",
            score=round(prediction, 4),
            confidence=0.9,  # CNN typically has high confidence
            details={
                "raw_prediction": round(prediction, 6),
                "model_params": f"~{_model.count_params():,}",
                "input_shape": "128x128x3",
            },
        )

    except Exception as e:
        return EngineResult(
            engine_name="CNN Classifier",
            score=0.0,
            confidence=0.0,
            error=str(e),
        )
# trigger reload
