"""
Ensemble Classifier for StegoHunter.

Combines multiple detection engines (Chi-Square, RS, SPA, DCT, Visual Attack)
and optionally a CNN classifier using a Weighted Quorum strategy.

STRATEGY: Weighted Average with Quorum Gate
- The final score is a weighted average of ALL engines
- An image is only flagged as stego if BOTH conditions are met:
  1. The weighted average exceeds the threshold (0.65)
  2. At least 2 primary engines independently flag it as suspicious (score > 0.4)
  
This prevents a single poorly-calibrated engine (like an untrained CNN)
from unilaterally flagging every image as a threat.
"""

from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2

from app.engines.base import EngineResult
from app.engines.chi_square import ChiSquareEngine
from app.engines.rs_analysis import RSAnalysisEngine
from app.engines.spa_analysis import SPAEngine
from app.engines.dct_analysis import DCTAnalysisEngine
from app.engines.visual_attack import VisualAttackEngine


@dataclass
class EnsembleResult:
    """Final result from the ensemble classifier."""
    is_stego: bool
    confidence: float
    threat_level: str  # "none", "low", "medium", "high", "critical"
    ensemble_score: float
    threshold: float
    engine_results: List[dict] = field(default_factory=list)
    detection_methods: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_stego": self.is_stego,
            "confidence": self.confidence,
            "threat_level": self.threat_level,
            "ensemble_score": self.ensemble_score,
            "threshold": self.threshold,
            "engine_results": self.engine_results,
            "detection_methods": self.detection_methods,
        }


class EnsembleClassifier:
    """
    Combines multiple detection engines with Weighted Quorum scoring.

    Weights:
    - Chi-Square: 25%
    - RS Analysis: 25%
    - SPA Analysis: 25%
    - DCT Analysis: 15%
    - Visual Attack: 10% (supplementary, reduced influence)
    - CNN: 10% (only if available and well-calibrated)
    
    Quorum Gate: At least 2 engines must independently score > 0.4
    to confirm a stego detection.
    """

    SUSPICION_THRESHOLD = 0.4  # Per-engine threshold to count as "suspicious"
    QUORUM_COUNT = 2           # Min engines that must agree before flagging

    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

        # Check if CNN is available
        from app.classifiers.cnn_clf import is_cnn_available, predict as cnn_predict
        self._cnn_predict = cnn_predict
        self._cnn_available = is_cnn_available()

        if self._cnn_available:
            # CNN gets only 10% — it's not well-calibrated enough to be trusted heavily
            self.engines = {
                "chi_square": {"engine": ChiSquareEngine(), "weight": 0.23},
                "rs_analysis": {"engine": RSAnalysisEngine(), "weight": 0.23},
                "spa":         {"engine": SPAEngine(),        "weight": 0.23},
                "dct":         {"engine": DCTAnalysisEngine(), "weight": 0.13},
            }
            self._visual_weight = 0.08
            self._cnn_weight = 0.10
            print("[Ensemble] CNN classifier is ACTIVE (10% weight, quorum-gated)")
        else:
            self.engines = {
                "chi_square": {"engine": ChiSquareEngine(), "weight": 0.28},
                "rs_analysis": {"engine": RSAnalysisEngine(), "weight": 0.27},
                "spa":         {"engine": SPAEngine(),        "weight": 0.27},
                "dct":         {"engine": DCTAnalysisEngine(), "weight": 0.18},
            }
            self._visual_weight = 0.0
            self._cnn_weight = 0.0
            print("[Ensemble] CNN classifier is DISABLED (no weights file)")

        # Supplementary engine
        self.visual_engine = VisualAttackEngine()

    def _classify_threat(self, score: float) -> str:
        """Map ensemble score to threat level."""
        if score < 0.3:
            return "none"
        elif score < 0.5:
            return "low"
        elif score < 0.65:
            return "medium"
        elif score < 0.85:
            return "high"
        else:
            return "critical"

    def analyze(self, image: np.ndarray) -> EnsembleResult:
        """
        Run all engines on the image and combine results using weighted quorum.

        Args:
            image: NumPy array (H, W, C) or (H, W) in uint8.

        Returns:
            EnsembleResult with combined detection verdict.
        """
        engine_results: List[dict] = []
        detection_methods: List[str] = []

        weighted_sum = 0.0
        total_weight = 0.0
        suspicious_count = 0  # Number of engines that independently flag stego

        # Run core statistical engines
        for key, entry in self.engines.items():
            engine = entry["engine"]
            weight = entry["weight"]

            result: EngineResult = engine.safe_analyze(image)

            result_dict = {
                "engine": result.engine_name,
                "score": result.score,
                "confidence": result.confidence,
                "details": result.details,
            }
            if result.error:
                result_dict["error"] = result.error

            engine_results.append(result_dict)

            if result.error is None:
                weighted_sum += result.score * weight
                total_weight += weight

                if result.score >= self.SUSPICION_THRESHOLD:
                    suspicious_count += 1
                    detection_methods.append(result.engine_name)

        # Run visual attack as supplementary
        visual_result = self.visual_engine.safe_analyze(image)
        engine_results.append({
            "engine": visual_result.engine_name,
            "score": visual_result.score,
            "confidence": visual_result.confidence,
            "details": visual_result.details,
            "error": visual_result.error,
            "is_supplementary": True,
        })

        if visual_result.error is None and self._visual_weight > 0:
            weighted_sum += visual_result.score * self._visual_weight
            total_weight += self._visual_weight
            if visual_result.score >= self.SUSPICION_THRESHOLD:
                suspicious_count += 1
                detection_methods.append(visual_result.engine_name)

        # Run CNN classifier if available
        if self._cnn_available:
            cnn_result = self._cnn_predict(image)
            if cnn_result is not None and cnn_result.error is None:
                engine_results.append({
                    "engine": cnn_result.engine_name,
                    "score": cnn_result.score,
                    "confidence": cnn_result.confidence,
                    "details": cnn_result.details,
                    "is_cnn": True,
                })
                weighted_sum += cnn_result.score * self._cnn_weight
                total_weight += self._cnn_weight
                if cnn_result.score >= self.SUSPICION_THRESHOLD:
                    suspicious_count += 1
                    detection_methods.append(cnn_result.engine_name)

        # --- HYBRID SCORING STRATEGY ---
        # 
        # Problem with pure weighted average: if an attacker uses an LSB method
        # that SPA and CNN detect at 70%+, but Chi-Square/RS/DCT don't detect 
        # (because they test for different algorithms), the 0% scores from 
        # those engines dilute the average to ~30% — a false negative.
        #
        # Solution: Conditional scoring based on quorum agreement.
        #
        # If QUORUM IS MET (≥2 engines score > 0.4):
        #   → Use the AVERAGE of only the suspicious engines as the score.
        #   → This prevents non-detecting engines from washing out real threats.
        #
        # If QUORUM IS NOT MET (<2 engines agree):
        #   → Use the global weighted average (naturally low = clean).
        #   → This prevents a single poorly-calibrated engine from causing FPs.

        # Collect scores from engines that independently flagged suspicion
        suspicious_scores = [
            r["score"] for r in engine_results
            if r.get("error") is None and r["score"] >= self.SUSPICION_THRESHOLD
        ]

        quorum_met = len(suspicious_scores) >= self.QUORUM_COUNT

        if quorum_met:
            # Multiple engines agree: use their average as the final score
            ensemble_score = round(float(np.mean(suspicious_scores)), 4)
        else:
            # No consensus: use the conservative global weighted average
            if total_weight > 0:
                ensemble_score = round(weighted_sum / total_weight, 4)
            else:
                ensemble_score = 0.0

        # Confidence: weighted average of engine confidences
        confidences = [
            r["confidence"] for r in engine_results
            if r.get("error") is None and not r.get("is_supplementary")
        ]
        overall_confidence = round(np.mean(confidences), 4) if confidences else 0.0

        # Final classification
        is_stego = ensemble_score >= self.threshold
        threat_level = self._classify_threat(ensemble_score)

        return EnsembleResult(
            is_stego=is_stego,
            confidence=overall_confidence,
            threat_level=threat_level,
            ensemble_score=ensemble_score,
            threshold=self.threshold,
            engine_results=engine_results,
            detection_methods=detection_methods,
        )


# Module-level singleton for reuse
_classifier: Optional[EnsembleClassifier] = None


def get_ensemble_classifier(threshold: float = 0.65) -> EnsembleClassifier:
    """Get or create the ensemble classifier singleton."""
    global _classifier
    if _classifier is None or _classifier.threshold != threshold:
        _classifier = EnsembleClassifier(threshold=threshold)
    return _classifier
