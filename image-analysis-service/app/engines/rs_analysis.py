"""
RS (Regular-Singular) Analysis Engine for LSB steganography detection.

RS Analysis divides the image into groups of pixels and classifies each group
as Regular (R), Singular (S), or Unusable (U) based on a discrimination function.
In clean images, R_m ≈ R_{-m} and S_m ≈ S_{-m}. LSB embedding disrupts this symmetry.

Reference: Fridrich, Goljan, Du - "Reliable Detection of LSB Steganography
in Color and Grayscale Images" (2001)
"""

import numpy as np
from app.engines.base import BaseEngine, EngineResult


class RSAnalysisEngine(BaseEngine):
    """
    Detects LSB steganography using Regular-Singular group analysis.

    The RS attack works by:
    1. Dividing pixels into groups
    2. Applying a flipping mask and its negative
    3. Computing a discrimination function (smoothness)
    4. Classifying groups as Regular, Singular, or Unusable
    5. Comparing R/S ratios for positive and negative masks
    """

    @property
    def name(self) -> str:
        return "RS Analysis"

    def _discrimination_function(self, group: np.ndarray) -> float:
        """Calculate smoothness of a pixel group (sum of absolute differences)."""
        return float(np.sum(np.abs(np.diff(group.astype(np.float64)))))

    def _flip(self, value: int, mask_val: int) -> int:
        """Apply flipping function based on mask value."""
        if mask_val == 1:
            # F1: swap 2k <-> 2k+1
            if value % 2 == 0:
                return value + 1
            else:
                return value - 1
        elif mask_val == -1:
            # F-1: swap 2k-1 <-> 2k, 2k+1 <-> 2k+2
            return value + 1 if value % 2 == 1 else value - 1
        return value

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
        group_size = 4  # Analyze in groups of 4 pixels
        mask_positive = np.array([0, 1, 1, 0])
        mask_negative = -mask_positive

        r_m, s_m = 0, 0      # Regular and Singular with positive mask
        r_neg_m, s_neg_m = 0, 0  # Regular and Singular with negative mask
        total_groups = 0

        # Process row by row in non-overlapping groups
        for y in range(height):
            row = gray[y, :]
            for x in range(0, width - group_size + 1, group_size):
                group = row[x: x + group_size].copy()
                f_original = self._discrimination_function(group)
                total_groups += 1

                # Apply positive mask
                flipped_pos = group.copy()
                for i in range(group_size):
                    if mask_positive[i] != 0:
                        val = int(flipped_pos[i])
                        flipped_pos[i] = np.clip(
                            self._flip(val, mask_positive[i]), 0, 255
                        )
                f_pos = self._discrimination_function(flipped_pos)

                if f_pos > f_original:
                    r_m += 1
                elif f_pos < f_original:
                    s_m += 1

                # Apply negative mask
                flipped_neg = group.copy()
                for i in range(group_size):
                    if mask_negative[i] != 0:
                        val = int(flipped_neg[i])
                        flipped_neg[i] = np.clip(
                            self._flip(val, mask_negative[i]), 0, 255
                        )
                f_neg = self._discrimination_function(flipped_neg)

                if f_neg > f_original:
                    r_neg_m += 1
                elif f_neg < f_original:
                    s_neg_m += 1

        if total_groups == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Image too small for RS analysis",
            )

        # Normalize
        r_m_ratio = r_m / total_groups
        s_m_ratio = s_m / total_groups
        r_neg_ratio = r_neg_m / total_groups
        s_neg_ratio = s_neg_m / total_groups

        # In a clean image: R_m ≈ R_{-m} and S_m ≈ S_{-m}
        # Under LSB embedding: R_{-m} increases significantly, R_{-m} > R_m
        # The key discriminator is the difference between R_{-m} and R_m

        r_diff = abs(r_neg_ratio - r_m_ratio)
        s_diff = abs(s_neg_ratio - s_m_ratio)

        # Estimate embedding rate using the RS model
        # Large asymmetry between positive and negative mask results = stego
        # NOTE: Natural images can exhibit R asymmetries up to 0.05-0.08
        # due to quantization and compression artifacts.
        score = 0.0

        # Primary indicator: R_{-m} vs R_m asymmetry
        if r_diff > 0.20:
            score += 0.5
        elif r_diff > 0.12:
            score += 0.3
        elif r_diff > 0.08:
            score += 0.1

        # Secondary indicator: S_{-m} vs S_m asymmetry
        if s_diff > 0.15:
            score += 0.3
        elif s_diff > 0.10:
            score += 0.15
        elif s_diff > 0.06:
            score += 0.05

        # Additional: In stego images, R_{-m} > R_m typically
        if r_neg_ratio > r_m_ratio * 1.2:
            score += 0.2

        score = min(score, 1.0)
        confidence = min(total_groups / 5000.0, 1.0)

        return EngineResult(
            engine_name=self.name,
            score=round(score, 4),
            confidence=round(confidence, 4),
            details={
                "R_m": round(r_m_ratio, 4),
                "S_m": round(s_m_ratio, 4),
                "R_neg_m": round(r_neg_ratio, 4),
                "S_neg_m": round(s_neg_ratio, 4),
                "R_asymmetry": round(r_diff, 4),
                "S_asymmetry": round(s_diff, 4),
                "total_groups": total_groups,
            },
        )
