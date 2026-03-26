import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "StegoHunter Image Analysis Service"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))

    # Ensemble detection threshold
    DETECTION_THRESHOLD: float = float(os.getenv("DETECTION_THRESHOLD", "0.65"))

    # Weight factors for ensemble scoring
    CHI_SQUARE_WEIGHT: float = 0.30
    RS_ANALYSIS_WEIGHT: float = 0.25
    SPA_WEIGHT: float = 0.25
    DCT_WEIGHT: float = 0.20

    # Max file size (50MB)
    MAX_FILE_SIZE: int = 50 * 1024 * 1024


settings = Settings()
