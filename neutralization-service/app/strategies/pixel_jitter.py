import numpy as np
from PIL import Image
from app.strategies.base_strategy import NeutralizationStrategy

class PixelJitter(NeutralizationStrategy):
    """
    Pixel Jitter Strategy.
    
    Adds extremely subtle Gaussian noise to the image. 
    This technique is specifically designed to disrupt statistical profiles
    and deep learning anomalies without visibly degrading the image, defeating
    high-variance steganography detectors and breaking brittle spatial embeds.
    """
    
    def __init__(self, variance: float = 1.0):
        """
        Initialize the Jitter strategy.
        
        Args:
            variance (float): The variance of the Gaussian noise.
                              Normally kept <= 2 to avoid human-perceptible grain.
        """
        self.variance = variance

    @property
    def name(self) -> str:
        return "pixel_jitter"
        
    @property
    def description(self) -> str:
        return f"Adds subtle Gaussian noise (variance={self.variance}) to disrupt structural and deep learning statistical profiles."

    def apply(self, image: Image.Image) -> Image.Image:
        img_arr = np.array(image, dtype=np.int16)
        
        # Generate Gaussian noise mapping to image shape
        noise = np.random.normal(loc=0.0, scale=self.variance, size=img_arr.shape)
        
        # Add noise and clip values carefully to uint8 bounds
        noisy_arr = img_arr + noise
        np.clip(noisy_arr, 0, 255, out=noisy_arr)
        
        return Image.fromarray(noisy_arr.astype(np.uint8))
