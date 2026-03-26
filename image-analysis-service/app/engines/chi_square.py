"""
Chi-Square Analysis Engine for LSB steganography detection.

The chi-square test compares the distribution of pixel value pairs (2k, 2k+1)
against a theoretically expected uniform distribution. LSB embedding creates
characteristic statistical anomalies that this test detects.

Reference: Westfeld & Pfitzmann, "Attacks on Steganographic Systems" (1999)
"""

import numpy as np
from scipy import stats
from app.engines.base import BaseEngine, EngineResult


class ChiSquareEngine(BaseEngine):
    """
    Detects LSB steganography using chi-square statistical analysis.

    LSB embedding alters the least significant bits of pixel values,
    causing pairs of values (2k, 2k+1) to converge toward equal frequency.
    This test measures that convergence.
    """

    @property
    def name(self) -> str:
        return "Chi-Square Analysis"

    def analyze(self, image: np.ndarray) -> EngineResult:
        if image is None or image.size == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Empty image",
            )

        # Convert to grayscale if color
        if len(image.shape) == 3:
            gray = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray = image.astype(np.uint8)

        # Flatten pixel values
        pixels = gray.flatten()

        # Build histogram of pixel values (0-255)
        histogram = np.bincount(pixels, minlength=256).astype(np.float64)

        # Chi-square test on pairs of values (2k, 2k+1)
        # Under LSB embedding, pairs (2k, 2k+1) tend toward equal frequency
        p_values = []
        pair_ratios = []

        for k in range(128):
            observed = np.array([histogram[2 * k], histogram[2 * k + 1]])
            total = observed.sum()

            if total < 5:
                continue  # Skip pairs with too few samples

            expected = np.array([total / 2.0, total / 2.0])

            # Chi-square statistic for this pair
            chi2_stat = np.sum((observed - expected) ** 2 / expected)
            p_value = 1.0 - stats.chi2.cdf(chi2_stat, df=1)
            p_values.append(p_value)

            # Ratio: how close are the pair frequencies?
            if total > 0:
                ratio = min(observed) / max(observed) if max(observed) > 0 else 0
                pair_ratios.append(ratio)

        if not p_values:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Insufficient pixel data for analysis",
            )

        p_values = np.array(p_values)
        pair_ratios = np.array(pair_ratios)

        # High p-values across many pairs indicate LSB embedding
        # (pairs are suspiciously equal in frequency)
        avg_p_value = np.mean(p_values)
        high_p_ratio = np.mean(p_values > 0.05)  # Fraction of pairs that pass
        avg_pair_ratio = np.mean(pair_ratios)

        # Score: combine metrics
        # A clean image has varied pair ratios; stego has pairs close to 1:1
        # NOTE: Clean photographs with smooth gradients naturally have high p-values
        # and high pair ratios. Thresholds must account for this.
        score = 0.0

        # If most pairs have high p-values, the distribution is suspicious
        if high_p_ratio > 0.95:
            score += 0.4
        elif high_p_ratio > 0.85:
            score += 0.2
        elif high_p_ratio > 0.75:
            score += 0.1

        # If pair ratios are very close to 1.0, suspicious
        if avg_pair_ratio > 0.97:
            score += 0.35
        elif avg_pair_ratio > 0.92:
            score += 0.2
        elif avg_pair_ratio > 0.85:
            score += 0.1

        # Additional: overall p-value contribution
        if avg_p_value > 0.7:
            score += 0.25
        elif avg_p_value > 0.5:
            score += 0.1

        score = min(score, 1.0)

        confidence = min(len(p_values) / 100.0, 1.0)  # More pairs = more confident

        return EngineResult(
            engine_name=self.name,
            score=round(score, 4),
            confidence=round(confidence, 4),
            details={
                "avg_p_value": round(float(avg_p_value), 4),
                "high_p_ratio": round(float(high_p_ratio), 4),
                "avg_pair_ratio": round(float(avg_pair_ratio), 4),
                "pairs_analyzed": len(p_values),
            },
        )
