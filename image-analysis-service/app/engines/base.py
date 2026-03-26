"""
Base class for all steganography detection engines.
Each engine analyzes an image and returns a detection score between 0.0 and 1.0.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class EngineResult:
    """Result from a single detection engine."""
    engine_name: str
    score: float  # 0.0 (clean) to 1.0 (definitely stego)
    confidence: float  # How confident the engine is in this score
    details: dict = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def is_suspicious(self) -> bool:
        return self.score > 0.5


class BaseEngine(ABC):
    """Abstract base class for steganography detection engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this engine."""
        ...

    @abstractmethod
    def analyze(self, image: np.ndarray) -> EngineResult:
        """
        Analyze an image for steganographic content.

        Args:
            image: NumPy array of shape (H, W, C) in uint8, BGR format.

        Returns:
            EngineResult with a score from 0.0 (clean) to 1.0 (stego).
        """
        ...

    def safe_analyze(self, image: np.ndarray) -> EngineResult:
        """Wrapper that catches exceptions and returns an error result."""
        try:
            return self.analyze(image)
        except Exception as e:
            return EngineResult(
                engine_name=self.name,
                score=0.0,
                confidence=0.0,
                error=str(e),
            )
