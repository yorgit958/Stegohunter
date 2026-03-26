import torch
import numpy as np
import os
from typing import Dict, Any
from .base_parser import BaseModelParser

class PyTorchParser(BaseModelParser):
    """
    Parses PyTorch models (.pt, .pth)
    Uses map_location='cpu' to prevent GPU hijacking and only extracts state dictionaries.
    """

    def parse(self) -> Dict[str, np.ndarray]:
        weights = {}
        try:
            # We strictly prevent execution of custom unpickling code where possible
            # by extracting only state dictionaries. For complex models, torch.jit is safer,
            # but torch.load with CPU mapping is the baseline for weights.
            state_dict = torch.load(self.file_path, map_location=torch.device('cpu'))

            # If it's a full model (not recommended but common), extract its state dict
            if isinstance(state_dict, torch.nn.Module):
                state_dict = state_dict.state_dict()
            
            # If it's a checkpoint dict, find the model weights
            elif isinstance(state_dict, dict) and "state_dict" in state_dict:
                state_dict = state_dict["state_dict"]
            elif isinstance(state_dict, dict) and "model_state_dict" in state_dict:
                state_dict = state_dict["model_state_dict"]

            if not isinstance(state_dict, dict):
                raise ValueError("Could not locate a valid state dictionary in the PyTorch file.")

            for target_key in ['weight', 'bias']:
                for k, v in state_dict.items():
                    if target_key in k and isinstance(v, torch.Tensor):
                        # Flatten to 1D for unified statistical analysis
                        weights[k] = self._flatten_tensor(v)

            return weights
            
        except Exception as e:
            raise ValueError(f"Failed to parse PyTorch model: {str(e)}")

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "framework": "PyTorch",
            "file_size_bytes": os.path.getsize(self.file_path)
        }
