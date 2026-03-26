import numpy as np
from scipy.stats import entropy, skew, kurtosis
from typing import Dict, Any, List

class WeightDistributionAnalyzer:
    """
    Analyzes DNN weight tensors to detect steganography anomalies.
    Common stego techniques (LSB injection, quantization) alter the 
    statistical distribution of neural network weights.
    """

    def __init__(self, lsb_bits: int = 1):
        self.lsb_bits = lsb_bits

    def analyze(self, weights: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Analyzes all layers in the model for anomalous statistical properties.
        """
        layer_results = []
        overall_threat = False
        max_entropy = 0.0

        for layer_name, tensor in weights.items():
            if len(tensor) < 500:
                continue # Skip small layers like bias vectors

            stats = self._analyze_layer(tensor)
            
            result = {
                "layer": layer_name,
                "size": len(tensor),
                "lsb_entropy": float(stats["entropy"]),
                "skewness": float(stats["skewness"]),
                "kurtosis": float(stats["kurtosis"]),
                "is_anomalous": bool(stats["is_anomalous"])
            }
            layer_results.append(result)

            if stats["is_anomalous"]:
                overall_threat = True
            if stats["entropy"] > max_entropy:
                max_entropy = float(stats["entropy"])

        return {
            "threat_detected": overall_threat,
            "max_lsb_entropy": max_entropy,
            "analyzed_layers": len(layer_results),
            "layer_results": sorted(layer_results, key=lambda x: x["lsb_entropy"], reverse=True)
        }

    def _analyze_layer(self, tensor: np.ndarray) -> Dict[str, float]:
        """
        Extract statistical moments and LSB entropy from a single layer.
        """
        # 1. Float32 to UInt32 raw bit conversion to access LSB
        raw_bits = tensor.view(np.uint32)
        
        # Extract the lowest 'lsb_bits'
        mask = (1 << self.lsb_bits) - 1
        lsbs = raw_bits & mask

        # Calculate Shannon Entropy of the LSBs
        # For 1 bit, values are 0 or 1.
        counts = np.bincount(lsbs, minlength=1<<self.lsb_bits)
        probs = counts / np.sum(counts)
        # Normalize entropy to [0.0, 1.0] by dividing by log2(states)
        # For 1 bit, max entropy is log2(2) = 1.0. For 2 bits, log2(4) = 2.0.
        ent = entropy(probs, base=2) / np.log2(1 << self.lsb_bits)

        # 2. Statistical Moments (Normal DNN weights are usually gaussian/laplacian)
        # Significant skewness or kurtosis deviation can indicate capacity hiding
        sk = skew(tensor, nan_policy='omit')
        ku = kurtosis(tensor, fisher=True, nan_policy='omit') # Fisher=True means normal is 0.0

        # Heuristics for Anomaly
        # Normally, LSB of IEEE-754 floats in SGD-trained models hover around 0.5-0.9 entropy.
        # Encrypted payload injection pushes this to practically 1.0 (perfect randomness).
        # We flag layers that are suspiciously close to perfect entropy (e.g. > 0.999).
        is_anomalous = ent > 0.999
        
        # Heavy artificial kurtosis > 15 (huge tails/spikes) or high skewness > 5
        if abs(sk) > 5.0 or ku > 15.0:
            is_anomalous = True

        return {
            "entropy": ent,
            "skewness": sk if not np.isnan(sk) else 0.0,
            "kurtosis": ku if not np.isnan(ku) else 0.0,
            "is_anomalous": is_anomalous
        }
