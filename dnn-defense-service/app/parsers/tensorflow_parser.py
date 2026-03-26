import h5py
import numpy as np
import os
from typing import Dict, Any
from .base_parser import BaseModelParser

class TensorFlowParser(BaseModelParser):
    """
    Parses TensorFlow/Keras HDF5 models (.h5)
    Safely walks the HDF5 group structure to extract layer weights without loading TF.
    """

    def parse(self) -> Dict[str, np.ndarray]:
        weights = {}
        
        def _extract_dataset(name, node):
            if isinstance(node, h5py.Dataset):
                # Filter for datasets that look like weights or biases
                lname = name.lower()
                if 'weight' in lname or 'kernel' in lname or 'bias' in lname:
                    data = node[:]
                    # Flatten securely
                    weights[name] = data.astype(np.float32).flatten()

        try:
            with h5py.File(self.file_path, 'r') as f:
                # Keras models store weights in a specific group usually
                if 'model_weights' in f:
                    f['model_weights'].visititems(_extract_dataset)
                else:
                    # Fallback to scanning everything (h5 weights only file)
                    f.visititems(_extract_dataset)
                    
            return weights
            
        except Exception as e:
            raise ValueError(f"Failed to parse TensorFlow HDF5 model: {str(e)}")

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "framework": "TensorFlow/Keras",
            "file_size_bytes": os.path.getsize(self.file_path)
        }
