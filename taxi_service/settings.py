from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DISPATCH_URL: str = "http://dispatch:8000"
    GRID_SIZE: int = 100
    TAXI_PORT: int = 8080

    class Config:
        env_file = ".env"

settings = Settings()