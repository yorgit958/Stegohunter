import io
from PIL import Image
from app.strategies.base_strategy import NeutralizationStrategy

class DCTReencoder(NeutralizationStrategy):
    """
    DCT (Discrete Cosine Transform) Re-encoder Strategy.
    
    This strategy destroys frequency-domain payloads (found in JPEGs) by forcing 
    the image to be decoded to raw pixels and then re-compressed using a different 
    quantization table (quality factor). This scrambles the specific coefficient 
    configurations required for algorithms like J-Steg, F5, or OutGuess.
    """
    
    def __init__(self, quality: int = 85):
        """
        Initialize the re-encoder.
        
        Args:
            quality (int): The target JPEG quality factor for the re-encoding (1-100).
                           Using a value different from the original image guarantees
                           coefficient scrambling. 85 is a good balance of quality
                           and sanitization.
        """
        self.quality = quality

    @property
    def name(self) -> str:
        return "dct_reencoder"
        
    @property
    def description(self) -> str:
        return f"Forces JPEG decoding and re-quantization at quality={self.quality} to scramble DCT coefficients."

    def apply(self, image: Image.Image) -> Image.Image:
        # If the image has an alpha channel (RGBA/LA), we must convert it to RGB 
        # before we can encode it as a JPEG (JPEG does not support transparency).
        mode = image.mode
        if mode in ('RGBA', 'LA') or (mode == 'P' and 'transparency' in image.info):
            # Create a white background and composite to avoid black backgrounds
            bg = Image.new('RGB', image.size, (255, 255, 255))
            if mode == 'P':
                image = image.convert('RGBA')
            bg.paste(image, mask=image.split()[-1])
            proc_image = bg
        else:
            proc_image = image.convert('RGB')
            
        # Re-encode to an in-memory JPEG buffer
        buffer = io.BytesIO()
        proc_image.save(buffer, format="JPEG", quality=self.quality, subsampling=1)
        buffer.seek(0)
        
        # Load the newly encoded image back into a PIL Image
        # We must make a copy so the buffer isn't required to stay open
        scrubbed_image = Image.open(buffer).copy()
        
        return scrubbed_image
