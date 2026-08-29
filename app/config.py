import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Pyrix"
    APP_ENV: str = "production"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # MS SQL Server settings
    DB_SERVER: str = "192.168.1.82"
    DB_PORT: int = 1433
    DB_USER: str = "sa"
    DB_PASSWORD: str = "Ho@mis*82"
    DB_NAME: str = "PyrixDB"
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE: str = "yes"
    DB_CONNECTION_TIMEOUT: int = 5

    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER},{self.DB_PORT};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            f"TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE};"
            f"Timeout={self.DB_CONNECTION_TIMEOUT};"
        )

    @property
    def master_connection_string(self) -> str:
        return (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER},{self.DB_PORT};"
            f"DATABASE=master;"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            f"TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE};"
            f"Timeout={self.DB_CONNECTION_TIMEOUT};"
        )

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
