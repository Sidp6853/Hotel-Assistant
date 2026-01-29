"""
Configuration settings for the Hotel Complaint Agent System
"""
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DB_PATH: Path = DATA_DIR / "hotel_complaints.db"  # Add this
    DATABASE_PATH: Path = DATA_DIR / "hotel_complaints.db"  # Alias for compatibility
    POLICIES_PATH: Path = PROJECT_ROOT / "config" / "hotel_policies.json"
    OUTPUT_DIR: Path = DATA_DIR / "sample_outputs"
    
    # LLM Configuration
    LLM_MODEL: str = "llama3.2:3b"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 512
    
    # RAG Configuration
    RAG_ENABLED: bool = True
    RAG_COLLECTION_NAME: str = "hotel_policies"
    RAG_TOP_K: int = 2
    
    # Pattern Detection
    PATTERN_DETECTION_ENABLED: bool = True
    RECURRING_GUEST_THRESHOLD: int = 2
    RECURRING_ROOM_THRESHOLD: int = 2
    
    # Notification Configuration
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_SLACK_NOTIFICATIONS: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(exist_ok=True)
settings.OUTPUT_DIR.mkdir(exist_ok=True)