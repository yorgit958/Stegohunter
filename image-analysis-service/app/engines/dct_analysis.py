"""
DCT (Discrete Cosine Transform) Analysis Engine for JPEG steganography detection.

Analyzes the DCT coefficient distribution in images to detect steganographic
modifications. JPEG steganography tools like JSteg, F5, and OutGuess modify
DCT coefficients, which creates detectable statistical anomalies.

This engine works on any image format by computing its own DCT,
not relying on JPEG's stored coefficients.
"""

import numpy as np
from app.engines.base import BaseEngine, EngineResult


class DCTAnalysisEngine(BaseEngine):
    """
    Detects steganography by analyzing DCT coefficient distributions.

    Examines:
    1. Histogram of DCT coefficients for anomalies
    2. Ratio of zero vs non-zero AC coefficients
    3. Blockiness artifacts from coefficient modification
    """

    @property
    def name(self) -> str:
        return "DCT Analysis"

    def _compute_dct_block(self, block: np.ndarray) -> np.ndarray:
        """Compute 2D DCT of an 8x8 block using separable 1D DCTs."""
        from scipy.fftpack import dct
        return dct(dct(block.astype(np.float64), axis=0, norm='ortho'), axis=1, norm='ortho')

    def analyze(self, image: np.ndarray) -> EngineResult:
        if image is None or image.size == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Empty image",
            )

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = np.mean(image, axis=2).astype(np.float64)
        else:
            gray = image.astype(np.float64)

        height, width = gray.shape

        # Need at least 8x8 for DCT analysis
        if height < 8 or width < 8:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="Image too small for DCT analysis (minimum 8x8)",
            )

        # Process non-overlapping 8x8 blocks
        all_ac_coeffs = []
        block_count = 0

        for y in range(0, height - 7, 8):
            for x in range(0, width - 7, 8):
                block = gray[y:y + 8, x:x + 8]
                dct_block = self._compute_dct_block(block)

                # Collect AC coefficients (exclude DC at [0,0])
                ac = dct_block.flatten()[1:]  # Skip DC coefficient
                all_ac_coeffs.extend(ac.tolist())
                block_count += 1

        if block_count == 0:
            return EngineResult(
                engine_name=self.name, score=0.0, confidence=0.0,
                error="No 8x8 blocks could be processed",
            )

        ac_coeffs = np.array(all_ac_coeffs)

        # --- Feature 1: Zero coefficient ratio ---
        # Stego tools often modify non-zero coefficients, reducing the zero count
        zero_ratio = np.sum(np.abs(ac_coeffs) < 0.5) / len(ac_coeffs)

        # --- Feature 2: Histogram anomaly (coefficient symmetry) ---
        # Natural images have roughly symmetric DCT coefficient distributions
        # Embedding can break this symmetry, especially for small coefficients
        small_coeffs = ac_coeffs[np.abs(ac_coeffs) < 10]
        if len(small_coeffs) > 100:
            pos_count = np.sum(small_coeffs > 0)
            neg_count = np.sum(small_coeffs < 0)
            total_nonzero = pos_count + neg_count
            if total_nonzero > 0:
                symmetry_ratio = min(pos_count, neg_count) / max(pos_count, neg_count)
            else:
                symmetry_ratio = 1.0
        else:
            symmetry_ratio = 1.0

        # --- Feature 3: Coefficient pair analysis (for JSteg detection) ---
        # JSteg replaces LSBs of non-zero AC coefficients
        # This creates pairs: histogram[2k] ≈ histogram[2k+1] for small k
        rounded_coeffs = np.round(ac_coeffs).astype(np.int32)
        hist_range = range(-20, 21)
        coeff_hist = {}
        for v in hist_range:
            coeff_hist[v] = np.sum(rounded_coeffs == v)

        pair_similarity = []
        for k in range(-10, 10):
            if k == 0:
                continue
            a = coeff_hist.get(2 * k, 0)
            b = coeff_hist.get(2 * k + 1, 0)
            total = a + b
            if total > 10:
                pair_similarity.append(min(a, b) / max(a, b) if max(a, b) > 0 else 0)

        avg_pair_sim = np.mean(pair_similarity) if pair_similarity else 0.5

        # --- Feature 4: Blockiness measure ---
        # Measure block boundary discontinuity (stego can increase blockiness)
        boundary_diffs = []
        for y in range(8, height - 7, 8):
            row_diff = np.mean(np.abs(gray[y, :] - gray[y - 1, :]))
            boundary_diffs.append(row_diff)
        for x in range(8, width - 7, 8):
            col_diff = np.mean(np.abs(gray[:, x] - gray[:, x - 1]))
            boundary_diffs.append(col_diff)

        avg_blockiness = np.mean(boundary_diffs) if boundary_diffs else 0

        # --- Scoring ---
        score = 0.0

        # Low zero ratio = coefficients were modified
        if zero_ratio < 0.4:
            score += 0.25
        elif zero_ratio < 0.5:
            score += 0.15

        # High pair similarity indicates JSteg-like embedding
        if avg_pair_sim > 0.9:
            score += 0.35
        elif avg_pair_sim > 0.8:
            score += 0.2

        # Asymmetry in coefficient distribution
        if symmetry_ratio < 0.85:
            score += 0.2
        elif symmetry_ratio < 0.92:
            score += 0.1

        # Elevated blockiness
        if avg_blockiness > 15:
            score += 0.2
        elif avg_blockiness > 10:
            score += 0.1

        score = min(score, 1.0)
        confidence = min(block_count / 500.0, 1.0)

        return EngineResult(
            engine_name=self.name,
            score=round(score, 4),
            confidence=round(confidence, 4),
            details={
                "zero_coeff_ratio": round(float(zero_ratio), 4),
                "symmetry_ratio": round(float(symmetry_ratio), 4),
                "avg_pair_similarity": round(float(avg_pair_sim), 4),
                "avg_blockiness": round(float(avg_blockiness), 4),
                "blocks_analyzed": block_count,
                "total_ac_coefficients": len(ac_coeffs),
            },
        )
