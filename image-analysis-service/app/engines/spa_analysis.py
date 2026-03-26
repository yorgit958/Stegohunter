"""
Sample Pairs Analysis (SPA) Engine for LSB steganography detection.

SPA exploits the relationship between pairs of sample values to detect
LSB replacement. It examines how the correlation between adjacent pixels
changes under LSB flipping, providing a more accurate estimate of
the embedding rate than chi-square or RS analysis alone.

Reference: Dumitrescu, Wu, Wang - "Detection of LSB Steganography via
Sample Pair Analysis" (2003)
"""

import numpy as np
from app.engines.base import BaseEngine, EngineResult


class SPAEngine(BaseEngine):
    """
    Detects LSB steganography using Sample Pairs Analysis.

    Classifies pixel pairs into categories based on LSB relationships
    and detects the statistical anomalies created by LSB embedding.
    """

    @property
    def name(self) -> str:
        return "SPA Analysis"

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

        pixels = gray.flatten().astype(np.int32)
        n = len(pixels)

        if n < 10:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Too few pixels",
            )

        # Trace close pairs (horizontally adjacent)
        # Category definitions for pair (u, v):
        #   X: same even pair (2k, 2k)
        #   Y: same odd pair (2k+1, 2k+1)
        #   W: adjacent pair where |u-v| = 1 and min is even
        #   Z: adjacent pair where |u-v| = 1 and min is odd

        # Analyze horizontal adjacent pairs
        u = pixels[:-1]
        v = pixels[1:]

        diff = np.abs(u - v)
        u_mod2 = u % 2
        v_mod2 = v % 2

        # Close pairs (|u-v| <= 1)
        close_mask = diff <= 1

        # Count pair types in close pairs
        same_even = np.sum((u == v) & (u_mod2 == 0))  # X
        same_odd = np.sum((u == v) & (u_mod2 == 1))    # Y

        adj_pairs = diff == 1
        min_vals = np.minimum(u, v)
        min_even = (min_vals % 2 == 0)

        w_count = np.sum(adj_pairs & min_even)  # W: min is even
        z_count = np.sum(adj_pairs & ~min_even)  # Z: min is odd

        total_pairs = n - 1

        if total_pairs == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="No pairs to analyze",
            )

        # In a clean image: X ≈ Y and W ≈ Z
        # After LSB embedding: the symmetry between (X,Y) and (W,Z) breaks
        # specifically, X+W ≈ Y+Z in clean images

        x_r = same_even / total_pairs
        y_r = same_odd / total_pairs
        w_r = w_count / total_pairs
        z_r = z_count / total_pairs

        # Asymmetry measures
        xy_diff = abs(x_r - y_r)
        wz_diff = abs(w_r - z_r)

        # Combined diagnostic
        # In a clean image, x_r ≈ y_r and w_r ≈ z_r
        # Under embedding, x+z changes relative to y+w
        xz = x_r + z_r
        yw = y_r + w_r
        combined_diff = abs(xz - yw)

        # Trace analysis: compute embedding rate estimate
        # The larger the asymmetry, the higher the embedding rate
        # NOTE: Natural images can exhibit asymmetries up to 0.05-0.08 due to
        # PNG compression, camera sensor quantization, and color subsampling.
        # Thresholds MUST be set above these natural baselines to avoid false positives.
        score = 0.0

        if combined_diff > 0.15:
            score += 0.4
        elif combined_diff > 0.10:
            score += 0.25
        elif combined_diff > 0.07:
            score += 0.1

        if xy_diff > 0.12:
            score += 0.3
        elif xy_diff > 0.08:
            score += 0.15
        elif xy_diff > 0.06:
            score += 0.05

        if wz_diff > 0.12:
            score += 0.3
        elif wz_diff > 0.08:
            score += 0.15
        elif wz_diff > 0.06:
            score += 0.05

        score = min(score, 1.0)
        confidence = min(total_pairs / 50000.0, 1.0)

        return EngineResult(
            engine_name=self.name,
            score=round(score, 4),
            confidence=round(confidence, 4),
            details={
                "X_ratio": round(float(x_r), 6),
                "Y_ratio": round(float(y_r), 6),
                "W_ratio": round(float(w_r), 6),
                "Z_ratio": round(float(z_r), 6),
                "XY_asymmetry": round(float(xy_diff), 6),
                "WZ_asymmetry": round(float(wz_diff), 6),
                "combined_asymmetry": round(float(combined_diff), 6),
                "total_pairs": total_pairs,
            },
        )
