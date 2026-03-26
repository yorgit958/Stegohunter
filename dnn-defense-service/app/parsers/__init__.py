from .base_parser import BaseModelParser
from .pytorch_parser import PyTorchParser
from .tensorflow_parser import TensorFlowParser
from .safetensors_parser import SafeTensorsParser
import os

def get_parser(file_path: str) -> BaseModelParser:
    """
    Returns the appropriate model parser based on the file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.pt', '.pth']:
        return PyTorchParser(file_path)
    elif ext in ['.h5', '.hdf5', '.keras']:
        return TensorFlowParser(file_path)
    elif ext in ['.safetensors']:
        return SafeTensorsParser(file_path)
    else:
        raise ValueError(f"Unsupported model file extension: {ext}")
