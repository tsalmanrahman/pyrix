import time
from typing import List, Dict, Any
from app.core.db import db
from app.config import get_settings

settings = get_settings()

class SQLInspectorService:
    @staticmethod
    def get_server_overview() -> Dict[str, Any]:
        health = db.check_health()
        
        db_stats = db.query_one(
            """
            SELECT 
                d.name,
                d.create_date,
                d.compatibility_level,
                d.collation_name,
                d.state_desc,
                d.recovery_model_desc
            FROM sys.databases d
            WHERE d.name = DB_NAME()
            """
        ) or {}

        active_conns = db.query_one(
            """
            SELECT COUNT(*) AS active_sessions
            FROM sys.dm_exec_sessions
            WHERE is_user_process = 1
            """
        ) or {"active_sessions": 0}

        return {
            **health,
            "database_stats": db_stats,
            "active_sessions": active_conns.get("active_sessions", 1)
        }

    @staticmethod
    def get_tables_info() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT 
                t.name AS table_name,
                s.name AS schema_name,
                p.rows AS row_count,
                CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS total_space_mb,
                CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS used_space_mb
            FROM sys.tables t
            INNER JOIN sys.indexes i ON t.object_id = i.object_id
            INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
            INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
            LEFT OUTER JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE t.is_ms_shipped = 0 AND i.OBJECT_ID > 255 AND i.index_id <= 1
            GROUP BY t.name, s.name, p.rows
            ORDER BY p.rows DESC, t.name ASC
            """
        )

    @staticmethod
    def execute_custom_query(sql_query: str) -> Dict[str, Any]:
        start = time.time()
        # Security: restrict destructive server commands if needed
        sql_stripped = sql_query.strip().upper()
        if any(keyword in sql_stripped for keyword in ["DROP DATABASE", "SHUTDOWN"]):
            return {
                "success": False,
                "error": "Execution of destructive system commands is blocked for safety.",
                "rows": [],
                "columns": [],
                "elapsed_ms": 0
            }
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(sql_query)
                elapsed_ms = round((time.time() - start) * 1000, 2)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": rows[:100], # Cap at 100 preview rows
                        "total_returned": len(rows),
                        "elapsed_ms": elapsed_ms,
                        "error": None
                    }
                else:
                    return {
                        "success": True,
                        "columns": ["Result"],
                        "rows": [{"Result": f"Command executed successfully. Rows affected: {cursor.rowcount}"}],
                        "total_returned": cursor.rowcount,
                        "elapsed_ms": elapsed_ms,
                        "error": None
                    }
        except Exception as e:
            elapsed_ms = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "total_returned": 0,
                "elapsed_ms": elapsed_ms,
                "error": str(e)
            }
