"""
Visual Attack Engine for steganography detection.

Implements a visual inspection technique that isolates the LSB plane
of an image and analyzes its entropy and structure. In clean images,
the LSB plane appears random. In stego images, embedded data creates
visible patterns or reduces entropy in the LSB plane.
"""

import numpy as np
from app.engines.base import BaseEngine, EngineResult


class VisualAttackEngine(BaseEngine):
    """
    Analyzes the LSB plane visually/statistically for structure
    that indicates embedded data.
    """

    @property
    def name(self) -> str:
        return "Visual Attack"

    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of a binary/integer array."""
        values, counts = np.unique(data, return_counts=True)
        probs = counts / counts.sum()
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        return float(entropy)

    def analyze(self, image: np.ndarray) -> EngineResult:
        if image is None or image.size == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Empty image",
            )

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray = image.astype(np.uint8)

        height, width = gray.shape

        # Extract LSB plane
        lsb_plane = gray & 1  # Least significant bit

        # --- Feature 1: LSB plane entropy ---
        # Random LSB (clean) should have entropy ≈ 1.0
        # Structured embedding may reduce entropy
        lsb_entropy = self._calculate_entropy(lsb_plane.flatten())

        # --- Feature 2: LSB autocorrelation ---
        # Measure correlation between adjacent LSB values
        # Clean images have low correlation; sequential embedding creates patterns
        flat_lsb = lsb_plane.flatten().astype(np.float64)
        if len(flat_lsb) > 1:
            mean_lsb = np.mean(flat_lsb)
            var_lsb = np.var(flat_lsb)
            if var_lsb > 0:
                autocorr = np.mean(
                    (flat_lsb[:-1] - mean_lsb) * (flat_lsb[1:] - mean_lsb)
                ) / var_lsb
            else:
                autocorr = 0.0
        else:
            autocorr = 0.0

        # --- Feature 3: Block uniformity ---
        # Divide LSB plane into blocks and check variance across blocks
        block_size = 16
        block_means = []
        for y in range(0, height - block_size + 1, block_size):
            for x in range(0, width - block_size + 1, block_size):
                block = lsb_plane[y:y + block_size, x:x + block_size]
                block_means.append(np.mean(block))

        if block_means:
            block_variance = np.var(block_means)
            block_mean_avg = np.mean(block_means)
        else:
            block_variance = 0.0
            block_mean_avg = 0.5

        # --- Feature 4: Multi-bit plane analysis ---
        # Check higher bit planes too (bit 1, bit 2) for anomalies
        bit1_plane = (gray >> 1) & 1
        bit1_entropy = self._calculate_entropy(bit1_plane.flatten())

        # Ratio of LSB entropy to bit-1 entropy
        # In clean images, both should be similar
        # In stego, LSB may be significantly different
        entropy_ratio = lsb_entropy / (bit1_entropy + 1e-10)

        # --- Scoring ---
        # NOTE: Clean images naturally have LSB entropy very close to 1.0 (random).
        # We should NOT penalize high entropy — that's the normal state.
        # Only penalize LOW entropy (structured data embedded) or high autocorrelation.
        score = 0.0

        # Entropy deviation: only flag significantly LOW entropy (structured payload)
        if lsb_entropy < 0.8:
            # Very low entropy = structured data in LSB plane
            score += 0.35
        elif lsb_entropy < 0.9:
            score += 0.15
        # Do NOT penalize high entropy (0.95-1.0) — that's normal for clean images

        # Autocorrelation: high positive = sequential embedding pattern
        abs_autocorr = abs(autocorr)
        if abs_autocorr > 0.10:
            score += 0.3
        elif abs_autocorr > 0.05:
            score += 0.15

        # Block variance: very low = uniform embedding across image
        if block_variance < 0.0005:
            score += 0.2
        elif block_variance < 0.002:
            score += 0.1

        # Entropy ratio anomaly (LSB vs bit-1 plane)
        if abs(entropy_ratio - 1.0) > 0.2:
            score += 0.15

        score = min(score, 1.0)
        total_pixels = height * width
        confidence = min(total_pixels / 100000.0, 1.0)

        return EngineResult(
            engine_name=self.name,
            score=round(score, 4),
            confidence=round(confidence, 4),
            details={
                "lsb_entropy": round(float(lsb_entropy), 4),
                "bit1_entropy": round(float(bit1_entropy), 4),
                "entropy_ratio": round(float(entropy_ratio), 4),
                "autocorrelation": round(float(autocorr), 6),
                "block_variance": round(float(block_variance), 6),
                "block_mean_avg": round(float(block_mean_avg), 4),
            },
        )
