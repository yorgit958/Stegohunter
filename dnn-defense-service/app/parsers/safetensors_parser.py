import numpy as np
import os
from typing import Dict, Any
from safetensors import safe_open
from .base_parser import BaseModelParser

class SafeTensorsParser(BaseModelParser):
    """
    Parses SafeTensors models (.safetensors)
    The most secure format, natively preventing arbitrary code execution.
    """

    def parse(self) -> Dict[str, np.ndarray]:
        weights = {}
        try:
            with safe_open(self.file_path, framework="pt", device="cpu") as f:
                # SafeTensors stores keys natively at the top level
                for key in f.keys():
                    tensor = f.get_tensor(key)
                    # For SafeTensors mapped to PyTorch, it returns a PyTorch tensor
                    weights[key] = self._flatten_tensor(tensor)

            return weights
            
        except Exception as e:
            raise ValueError(f"Failed to parse SafeTensors model: {str(e)}")

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "framework": "SafeTensors",
            "file_size_bytes": os.path.getsize(self.file_path)
        }
