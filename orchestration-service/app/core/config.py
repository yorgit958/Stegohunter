from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StegoHunter Orchestration Service"
    VERSION: str = "1.0.0"
    
    # Message Broker / Result Backend
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
settings = Settings()
