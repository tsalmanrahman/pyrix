from typing import List, Dict, Any
from app.core.db import db

class AuditService:
    @staticmethod
    def get_logs(limit: int = 50, action_filter: str = None) -> List[Dict[str, Any]]:
        if action_filter:
            return db.query(
                """
                SELECT TOP (?) * FROM audit_logs 
                WHERE action_type = ? 
                ORDER BY created_at DESC, log_id DESC
                """,
                (limit, action_filter)
            )
        return db.query(
            "SELECT TOP (?) * FROM audit_logs ORDER BY created_at DESC, log_id DESC",
            (limit,)
        )

    @staticmethod
    def clear_logs() -> bool:
        db.execute("TRUNCATE TABLE audit_logs")
        return True
