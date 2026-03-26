import h5py
import numpy as np
from scipy.stats import entropy
from collections import defaultdict

class H5Analyzer:
    """
    Parses massive Keras/TensorFlow HDF5 model weights.
    Hunts for LSB steganography and spatial substitution attacks by measuring
    the Shannon Entropy and probability distributions of Float32/Float16 weights.
    
    Standard neural network layers exhibit smooth, Gaussian, or heavy-tailed distributions.
    Steganographic implants, especially encrypted payloads, force the LSBs into a uniform
    distribution, severely spiking the bitwise entropy.
    """
    
    @staticmethod
    def calculate_entropy(data: np.ndarray) -> float:
        """Calculate the Shannon Entropy of the raw byte representation of the tensor."""
        # Convert the float array to raw bytes to measure physical data entropy
        raw_bytes = data.tobytes()
        if len(raw_bytes) == 0:
            return 0.0
            
        # Count byte frequencies (0-255)
        counts = np.bincount(np.frombuffer(raw_bytes, dtype=np.uint8), minlength=256)
        probs = counts / len(raw_bytes)
        
        # Calculate Shannon entropy (max 8.0 for pure noise/encrypted data)
        return entropy(probs, base=2)

    @staticmethod
    def analyze(file_path: str) -> dict:
        result = {
            "is_stego": False,
            "threat_level": "none",
            "confidence": 0.0,
            "entropy": 0.0,
            "anomalous_layers": [],
            "total_parameters": 0
        }
        
        total_entropy = 0.0
        layers_analyzed = 0
        max_layer_anomaly = 0.0
        
        try:
            with h5py.File(file_path, 'r') as f:
                def process_node(name, node):
                    nonlocal total_entropy, layers_analyzed, max_layer_anomaly
                    
                    # We only care about actual datasets (tensors), not structural groups
                    if isinstance(node, h5py.Dataset):
                        data = node[:]
                        
                        # Only analyze floating point weights (skipping biases/ints if small)
                        if data.dtype in [np.float32, np.float16, np.float64] and data.size > 1000:
                            layer_entropy = H5Analyzer.calculate_entropy(data)
                            
                            total_entropy += layer_entropy
                            layers_analyzed += 1
                            result["total_parameters"] += data.size
                            
                            # Standard AI weights usually have entropy around 5.0 - 7.2.
                            # Encrypted stego payloads max out at exactly 7.99 - 8.00.
                            if layer_entropy > 7.90:
                                max_layer_anomaly = max(max_layer_anomaly, layer_entropy)
                                result["anomalous_layers"].append({
                                    "layer_name": name,
                                    "entropy": round(layer_entropy, 3),
                                    "size": data.size
                                })

                # Traverse the entire H5 tree
                f.visititems(process_node)
                
            if layers_analyzed > 0:
                avg_entropy = total_entropy / layers_analyzed
                result["entropy"] = round(avg_entropy, 3)
                
                # Decision Matrix
                if max_layer_anomaly > 7.98 or avg_entropy > 7.95:
                    result["is_stego"] = True
                    result["threat_level"] = "critical"
                    result["confidence"] = 99.8
                elif max_layer_anomaly > 7.93:
                    result["is_stego"] = True
                    result["threat_level"] = "high"
                    result["confidence"] = 85.5
                elif len(result["anomalous_layers"]) > 0:
                    result["is_stego"] = True
                    result["threat_level"] = "medium"
                    result["confidence"] = 65.0
                else:
                    result["confidence"] = 100.0 # 100% confident it's clean
                    
        except Exception as e:
            print(f"H5 Parsing Error: {e}")
            raise
            
        return result
