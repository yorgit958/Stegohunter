from typing import Dict, Type
from app.strategies.base_strategy import NeutralizationStrategy
from app.strategies.lsb_scrubber import LSBScrubber
from app.strategies.dct_reencoder import DCTReencoder
from app.strategies.pixel_jitter import PixelJitter
from app.strategies.metadata_stripper import MetadataStripper
from app.strategies.composite_strategy import CompositeStrategy

class StrategyRegistry:
    """
    Singleton registry to store and instantiate neutralization strategies.
    """
    
    _strategies: Dict[str, Type[NeutralizationStrategy]] = {
        "lsb_scrubber": LSBScrubber,
        "dct_reencoder": DCTReencoder,
        "pixel_jitter": PixelJitter,
        "metadata_stripper": MetadataStripper,
    }

    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> NeutralizationStrategy:
        """Instantiate a strategy by name."""
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return cls._strategies[name](**kwargs)
        
    @classmethod
    def list_strategies(cls) -> list:
        """List all available strategies."""
        return list(cls._strategies.keys())
        
    @classmethod
    def build_composite(cls, names: list) -> CompositeStrategy:
        """Build a chain of specific strategies."""
        instances = [cls.get_strategy(n) for n in names]
        return CompositeStrategy(instances)
