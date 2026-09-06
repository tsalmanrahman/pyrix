import os
import sys
from typing import Optional
from functools import lru_cache
import pyodbc
from pydantic_settings import BaseSettings

def resolve_sql_driver(preferred: Optional[str] = None) -> str:
    """
    Dynamically auto-detects the best available SQL Server ODBC driver.
    Works seamlessly on Windows, macOS, and Linux without manual code changes.
    """
    try:
        available = pyodbc.drivers()
    except Exception:
        available = []

    # 1. If preferred exists on system, use it
    if preferred and preferred in available:
        return preferred

    # 2. Check prioritized list of drivers (modern to legacy)
    priorities = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "ODBC Driver 11 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server",
    ]
    for candidate in priorities:
        if candidate in available:
            return candidate

    # 3. macOS direct library fallback (if unixODBC odbcinst.ini has no name registered)
    if sys.platform == "darwin":
        mac_paths = [
            "/opt/homebrew/lib/libmsodbcsql.18.dylib",
            "/usr/local/lib/libmsodbcsql.18.dylib",
            "/opt/homebrew/lib/libmsodbcsql.17.dylib",
            "/usr/local/lib/libmsodbcsql.17.dylib",
        ]
        for path in mac_paths:
            if os.path.exists(path):
                return path

    return preferred or "ODBC Driver 18 for SQL Server"

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
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE: str = "yes"
    DB_CONNECTION_TIMEOUT: int = 5

    @property
    def resolved_driver(self) -> str:
        return resolve_sql_driver(self.DB_DRIVER)

    def _build_connection_string(self, database_name: str) -> str:
        driver = self.resolved_driver
        conn_parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={self.DB_SERVER},{self.DB_PORT}",
            f"DATABASE={database_name}",
            f"UID={self.DB_USER}",
            f"PWD={self.DB_PASSWORD}",
            f"Timeout={self.DB_CONNECTION_TIMEOUT}",
        ]
        # Driver 18 requires explicit encryption settings
        if "18" in driver:
            conn_parts.append("Encrypt=yes")
            conn_parts.append(f"TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE}")
        elif "17" in driver:
            conn_parts.append(f"TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE}")

        return ";".join(conn_parts) + ";"

    @property
    def connection_string(self) -> str:
        return self._build_connection_string(self.DB_NAME)

    @property
    def master_connection_string(self) -> str:
        return self._build_connection_string("master")

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
