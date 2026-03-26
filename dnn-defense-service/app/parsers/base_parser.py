import abc
import numpy as np
from typing import Dict, Any, Tuple

class BaseModelParser(abc.ABC):
    """
    Abstract base class for all DNN model parsers.
    Responsible for extracting weight tensors securely without fully executing the model code.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    @abc.abstractmethod
    def parse(self) -> Dict[str, np.ndarray]:
        """
        Extract weights from the model file.
        Returns a dictionary mapping layer/tensor names to flattened numpy arrays.
        """
        pass

    @abc.abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract basic metadata (framework, size, inferred architecture).
        """
        pass

    def _flatten_tensor(self, tensor: Any) -> np.ndarray:
        """
        Utility to flatten a tensor to a 1D numpy array of float32.
        """
        if isinstance(tensor, np.ndarray):
            return tensor.astype(np.float32).flatten()
            
        import torch
        if isinstance(tensor, torch.Tensor):
            return tensor.detach().cpu().numpy().astype(np.float32).flatten()
            
        raise ValueError(f"Unsupported tensor type: {type(tensor)}")
