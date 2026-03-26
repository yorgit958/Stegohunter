from typing import List
from app.selector.strategy_registry import StrategyRegistry
from app.strategies.base_strategy import NeutralizationStrategy

class StrategySelector:
    """
    Automatically selects the optimal neutralization strategy based on 
    the analytical results from the Image Analysis Service.
    """
    
    @staticmethod
    def select_optimal_strategies(analysis_results: dict) -> NeutralizationStrategy:
        """
        Maps detection threats to countermeasures.
        
        Args:
            analysis_results: The JSON payload returned by the Image Analysis Service.
            
        Returns:
            A NeutralizationStrategy instance (likely a CompositeStrategy).
        """
        selected_names = []
        
        # 1. ALWAYS strip metadata as a baseline defense
        selected_names.append("metadata_stripper")
        
        # Examine the triggered detection engines
        detection_methods = analysis_results.get("detection_methods", {}).get("methods_triggered", [])
        engines = analysis_results.get("detection_methods", {}).get("engines", [])
        
        # 2. Check for spatial-domain manipulation (Chi-Square, RS, SPA)
        spatial_threat = False
        for method in detection_methods:
            if method in ["Chi-Square Statistical Anomaly", "RS Analysis Anomaly", "SPA Structural Imbalance"]:
                spatial_threat = True
                
        if spatial_threat:
            selected_names.append("lsb_scrubber")
            
        # 3. Check for frequency-domain manipulation (DCT)
        dct_threat = False
        for method in detection_methods:
            if "DCT" in method:
                dct_threat = True
                
        if dct_threat:
            selected_names.append("dct_reencoder")
            
        # 4. Check deep learning thresholds / CNN
        cnn_score = 0
        for eng in engines:
            if eng.get("engine") == "CNN Classifier":
                cnn_score = eng.get("score", 0)
                
        if cnn_score > 0.65 or "Deep Learning Structure Anomaly" in detection_methods:
            # DNN-based stego is highly resilient but mathematically fragile to Gaussian Noise
            selected_names.append("pixel_jitter")
            
        # If no specific threat was found but we are neutralizing anyway,
        # apply a generic robust scrubber chain
        if len(selected_names) == 1:
            selected_names.extend(["lsb_scrubber", "pixel_jitter"])
            
        return StrategyRegistry.build_composite(selected_names)
