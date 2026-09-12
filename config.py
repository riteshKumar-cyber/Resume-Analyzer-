import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application Settings and Configuration."""
    
    BASE_DIR: Path = Path(__file__).resolve().parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # File validation limits
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".pdf"}
    ALLOWED_MIME_TYPES: set = {"application/pdf"}

settings = Settings()

# Ensure uploads directory exists on configuration import
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
