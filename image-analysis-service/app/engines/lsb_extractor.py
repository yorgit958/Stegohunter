import numpy as np
import string
import io
from PIL import Image

class LSBExtractor:
    """
    Attempts to extract human-readable ASCII payloads hidden in the LSB layer.
    Prioritizes the standard `stegano` library logic for classic strings, 
    falling back to a raw multidimensional bit-scraper for non-standard embeds.
    """
    
    @staticmethod
    def extract_ascii(image: np.ndarray, file_bytes: bytes = None) -> str:
        # First, try standard LSB extraction using stegano if file bytes were provided
        if file_bytes is not None:
            try:
                from stegano import lsb
                # It requires a readable buffer
                buffer = io.BytesIO(file_bytes)
                secret = lsb.reveal(buffer)
                if secret and len(secret.strip()) > 0:
                    return secret
            except Exception:
                pass # Fallback to raw bit scraping
                
        # --- Fallback: Raw Bit Scraper ---
        # Convert image to RGB if not already
        if len(image.shape) == 2:
            image = np.stack((image,)*3, axis=-1)
        elif image.shape[2] == 4:
            image = image[:, :, :3]  # Drop alpha
            
        # Flatten the image channels linearly: R1 G1 B1 R2 G2 B2 ...
        pixels = image.flatten()
        
        # Extract the least significant bit of each byte
        lsb_bits = pixels & 1
        
        # Pack bits into bytes (8 bits = 1 ASCII character)
        valid_len = (len(lsb_bits) // 8) * 8
        lsb_bits = lsb_bits[:valid_len]
        bytes_array = np.packbits(lsb_bits)
        
        # Limit extraction size to prevent massive memory hangs
        bytes_array = bytes_array[:2000]
        
        printable = set(string.printable.encode('ascii'))
        extracted_chars = []
        consecutive_nulls = 0
        
        for b in bytes_array:
            if b == 0:
                consecutive_nulls += 1
                if consecutive_nulls > 4: 
                    break # End of string
                continue
            
            consecutive_nulls = 0
            if b in printable:
                extracted_chars.append(chr(b))
                
        decoded_string = "".join(extracted_chars).strip()
        
        if len(decoded_string) < 3:
            return "No recognizable plaintext ASCII payload found. The data may be encrypted, compressed, or use non-linear embedding algorithms."
            
        return decoded_string
