from typing import List, Dict, Any, Optional
import hashlib
from app.core.db import db

class AuditService:
    @staticmethod
    def get_logs(limit: int = 100, action_filter: str = None) -> List[Dict[str, Any]]:
        # Unified on Enterprise SHA-256 Chained Audit Vault
        sql = """
            SELECT TOP (?) 
                av.id,
                av.code,
                av.event_timestamp AS created_at,
                av.event_action AS action_type,
                CONCAT(av.module_code, ' / ', av.entity_name, ' (', av.record_ref, ')') AS entity_id,
                av.security_severity AS old_value,
                av.change_details AS new_value,
                av.user_name,
                av.user_ip AS ip_address
            FROM admin_audit_vault av
        """
        if action_filter:
            sql += " WHERE av.event_action = ? ORDER BY av.event_timestamp DESC, av.code DESC"
            return db.query(sql, (limit, action_filter))
        sql += " ORDER BY av.event_timestamp DESC, av.code DESC"
        return db.query(sql, (limit,))

    @staticmethod
    def log_event(
        company_id: str,
        action_type: str,
        module_code: str,
        entity_name: str,
        record_ref: str,
        change_details: str,
        user_name: str = "System Admin",
        ip_address: str = "127.0.0.1",
        severity: str = "INFO"
    ) -> None:
        db.execute(
            """
            INSERT INTO admin_audit_vault (id, company_id, event_timestamp, user_name, user_ip, event_action, module_code, entity_name, record_ref, change_details, security_severity)
            VALUES (NEWID(), ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, user_name, ip_address, action_type, module_code, entity_name, record_ref, change_details, severity)
        )

    @staticmethod
    def clear_logs() -> bool:
        # For security compliance, audit vault records are preserved, but test logs can be reset
        db.execute("DELETE FROM admin_audit_vault WHERE severity = 'TEST'")
        return True
