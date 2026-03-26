from abc import ABC, abstractmethod
from PIL import Image

class NeutralizationStrategy(ABC):
    """
    Abstract base class for all steganography neutralization strategies.
    Strategies take an image and apply a transformation that destroys 
    hidden payloads while attempting to maintain visual fidelity.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the strategy."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of what the strategy does."""
        pass

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Apply the neutralization strategy to the provided image.
        
        Args:
            image (Image.Image): The loaded PIL Image object.
            
        Returns:
            Image.Image: The processed (scrubbed) PIL Image object.
        """
        pass
