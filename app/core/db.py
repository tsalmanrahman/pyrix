import time
import pyodbc
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from app.config import get_settings

settings = get_settings()

class DatabaseManager:
    """Thread-safe MS SQL Server query executor and connection manager."""

    @staticmethod
    def get_connection(use_master: bool = False, autocommit: bool = False) -> pyodbc.Connection:
        conn_str = settings.master_connection_string if use_master else settings.connection_string
        return pyodbc.connect(conn_str, autocommit=autocommit)

    @staticmethod
    @contextmanager
    def get_cursor(use_master: bool = False, commit: bool = True, autocommit: bool = False):
        conn = DatabaseManager.get_connection(use_master=use_master, autocommit=autocommit)
        cursor = conn.cursor()
        try:
            yield cursor
            if commit and not autocommit:
                conn.commit()
        except Exception:
            if not autocommit:
                conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def query(sql: str, params: Tuple = (), use_master: bool = False) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        with DatabaseManager.get_cursor(use_master=use_master, commit=False) as cursor:
            cursor.execute(sql, params)
            if cursor.description is None:
                return []
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results

    @staticmethod
    def query_one(sql: str, params: Tuple = (), use_master: bool = False) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query and returns a single row dictionary."""
        rows = DatabaseManager.query(sql, params, use_master=use_master)
        return rows[0] if rows else None

    @staticmethod
    def execute(sql: str, params: Tuple = (), use_master: bool = False) -> int:
        """Executes INSERT/UPDATE/DELETE and returns affected row count."""
        with DatabaseManager.get_cursor(use_master=use_master, commit=True) as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount

    @staticmethod
    def check_health() -> Dict[str, Any]:
        """Checks connection latency and server status."""
        start_time = time.time()
        try:
            info = DatabaseManager.query_one(
                "SELECT @@VERSION AS [version], @@SERVERNAME AS [servername], DB_NAME() AS [current_db]"
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "online",
                "latency_ms": latency_ms,
                "server": info["servername"] if info else settings.DB_SERVER,
                "database": info["current_db"] if info else settings.DB_NAME,
                "version": info["version"] if info else "Unknown",
                "error": None
            }
        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "offline",
                "latency_ms": latency_ms,
                "server": settings.DB_SERVER,
                "database": settings.DB_NAME,
                "version": None,
                "error": str(e)
            }

db = DatabaseManager()
