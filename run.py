#!/usr/bin/env python
"""
Pyrix Application Launcher
Starts the Uvicorn ASGI server with live reload enabled.
"""
import uvicorn
from app.config import get_settings

def main():
    settings = get_settings()
    print("=" * 60)
    print("Pyrix - Modern Dynamic Operations & Settings")
    print(f"SQL Server Target: {settings.DB_SERVER}:{settings.DB_PORT} ({settings.DB_NAME})")
    print(f"Local Address:     http://localhost:{settings.PORT}")
    print(f"Network Address:   http://{settings.HOST}:{settings.PORT}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=["app"],
        reload_includes=["*.py", "*.html", "*.css", "*.js"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
