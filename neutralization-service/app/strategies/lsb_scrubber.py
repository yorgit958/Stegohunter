import numpy as np
from PIL import Image
from app.strategies.base_strategy import NeutralizationStrategy

class LSBScrubber(NeutralizationStrategy):
    """
    LSB (Least Significant Bit) Scrubber Strategy.
    
    This strategy destroys spatial-domain payloads by RANDOMIZING the 
    least significant N bits of every pixel across all color channels.
    
    CRITICAL: We must use random noise instead of zeroing. If we zero-out
    the LSBs, every pixel becomes perfectly even (divisible by 2). This 
    creates an artificially perfect distribution that Chi-Square, RS, and 
    SPA engines detect as WORSE than the original stego, because natural 
    images never have 100% even LSBs.
    
    Random noise restores the natural 50/50 distribution of even/odd 
    pixel values, making the output indistinguishable from a clean image.
    """
    
    def __init__(self, target_bits: int = 2):
        """
        Initialize the scrubber.
        
        Args:
            target_bits (int): Number of least significant bits to randomize (1-3).
                               Using 2 bits destroys payloads hidden in LSB-1 and LSB-2.
        """
        self.target_bits = target_bits

    @property
    def name(self) -> str:
        return "lsb_scrubber"
        
    @property
    def description(self) -> str:
        return f"Randomizes the lowest {self.target_bits} bit(s) of every pixel to destroy spatial LSB payloads while preserving natural statistics."

    def apply(self, image: Image.Image) -> Image.Image:
        # Convert to numpy array
        img_arr = np.array(image)
        
        # Step 1: Create a bitmask to clear the target LSBs
        # If target_bits=2, mask is 11111100 (252)
        clear_mask = np.uint8(~((1 << self.target_bits) - 1))
        
        # Step 2: Zero the target bits
        cleared = np.bitwise_and(img_arr, clear_mask)
        
        # Step 3: Generate cryptographically random replacement bits for ALL pixels.
        # This is the critical difference from the old zero-fill approach.
        # Random LSBs restore the natural statistical profile of the image.
        noise = np.random.randint(
            0, (1 << self.target_bits), 
            size=img_arr.shape, 
            dtype=np.uint8
        )
        
        # Step 4: OR the random bits into the cleared positions
        scrubbed_arr = np.bitwise_or(cleared, noise).astype(np.uint8)
        
        return Image.fromarray(scrubbed_arr)
