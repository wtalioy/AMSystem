import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import ConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="ignore")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Database
    DB_DRIVER: str = os.getenv("DRIVER", "")
    DB_SERVER: str = os.getenv("SERVER", "")
    DB_DATABASE: str = os.getenv("DATABASE", "")
    DB_UID: str = os.getenv("UID", "")
    DB_PWD: str = os.getenv("PWD", "")

settings = Settings()
