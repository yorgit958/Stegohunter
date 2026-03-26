from PIL import Image
from app.strategies.base_strategy import NeutralizationStrategy

class MetadataStripper(NeutralizationStrategy):
    """
    Metadata Stripper Strategy.
    
    This strategy removes all EXIF, ICC profiles, and arbitrary chunks 
    appended to the file format wrapper, without altering the actual pixel data.
    """
    
    @property
    def name(self) -> str:
        return "metadata_stripper"
        
    @property
    def description(self) -> str:
        return "Strips EXIF data and other non-pixel metadata chunks from the file."

    def apply(self, image: Image.Image) -> Image.Image:
        # Create a completely new image from the raw pixel data
        # 'copy()' clones the pixel data, but not the 'info' metadata dictionary
        # unless specifically designed to. Pilot library usually leaves 'info'.
        # To be safe, we explicitly clear the info dictionary.
        
        data = list(image.getdata())
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(data)
        
        # Ensure info dict is completely empty
        clean_image.info = {}
        
        return clean_image
