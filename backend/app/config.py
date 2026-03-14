import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/companycam")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours


settings = Settings()
