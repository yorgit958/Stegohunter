from typing import List
from PIL import Image
from app.strategies.base_strategy import NeutralizationStrategy

class CompositeStrategy(NeutralizationStrategy):
    """
    Composite Strategy chain.
    
    Execute a series of strategies in order. This handles combining
    defenses, like first stripping Metadata, then scrubbing LSB, 
    and finally re-encoding DCT.
    """
    
    def __init__(self, strategies: List[NeutralizationStrategy]):
        self.strategies = strategies

    @property
    def name(self) -> str:
        return "composite_chain"
        
    @property
    def description(self) -> str:
        names = ", ".join([s.name for s in self.strategies])
        return f"Applies a sequenced chain of defenses: {names}"

    def apply(self, image: Image.Image) -> Image.Image:
        current_image = image
        
        for strategy in self.strategies:
            current_image = strategy.apply(current_image)
            
        return current_image
