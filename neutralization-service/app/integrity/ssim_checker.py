import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import mean_squared_error as mse

class IntegrityChecker:
    """
    Validates that a neutralized image maintains sufficient visual 
    fidelity compared to the original image.
    """
    
    def __init__(self, min_ssim: float = 0.95, min_psnr: float = 35.0):
        self.min_ssim = min_ssim
        self.min_psnr = min_psnr

    def evaluate(self, original: Image.Image, scrubbed: Image.Image) -> dict:
        """
        Calculates SSIM, PSNR, and MSE metrics between original and scrubbed images.
        """
        # Ensure identical sizes
        if original.size != scrubbed.size:
            scrubbed = scrubbed.resize(original.size)
            
        # Convert to numpy arrays
        # SSIM works best on grayscale or with channel_axis specified.
        # For simplicity and speed, we evaluate on the luminance (grayscale) channel.
        orig_gray = np.array(original.convert('L'))
        scr_gray = np.array(scrubbed.convert('L'))
        
        # Calculate metrics
        ssim_val = ssim(orig_gray, scr_gray, data_range=scr_gray.max() - scr_gray.min())
        
        # Calculate PSNR and MSE
        # MSE can be 0 if perfectly identical, handle division by zero in PSNR
        mse_val = mse(orig_gray, scr_gray)
        if mse_val == 0:
            psnr_val = 100.0  # arbitrary high value for identical images
        else:
            psnr_val = psnr(orig_gray, scr_gray, data_range=255)
            
        passed = float(ssim_val) >= self.min_ssim and float(psnr_val) >= self.min_psnr
        
        return {
            "ssim": float(ssim_val),
            "psnr_db": float(psnr_val),
            "mse": float(mse_val),
            "passed": passed,
            "quality_approved": passed,
        }
