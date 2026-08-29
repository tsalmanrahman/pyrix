from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

MODULE_SHORT_CODES = {
    "general-ledger": "GL",
    "accounts-receivable": "AR",
    "accounts-payable": "AP",
    "cash-book": "CB",
    "sourcing": "SOURCING",
    "inventory": "INV",
    "sales": "SALES",
    "distribution": "DIST",
    "cnf-jobs": "CNF",
    "mrp-planning": "MRP",
    "production": "PROD",
    "fixed-assets": "FA",
    "property-sales": "PROP-SALES",
    "property-dev": "PROP-DEV",
    "property-cost": "PROP-COST",
    "construction": "CONST",
    "hris": "HRIS",
    "crm": "CRM",
    "admin-functions": "ADMIN",
    "system-admin": "SYS",
}

class EnterpriseModuleService:
    @staticmethod
    def _enrich_module(m: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not m:
            return None
        slug = m.get("route_slug", "")
        m["short_code"] = MODULE_SHORT_CODES.get(slug, m.get("module_code", "MOD"))
        return m

    @staticmethod
    def get_all_modules() -> List[Dict[str, Any]]:
        modules = db.query(
            "SELECT * FROM enterprise_modules WHERE is_enabled = 1 ORDER BY sort_order ASC, code ASC"
        )
        return [EnterpriseModuleService._enrich_module(m) for m in modules]

    @staticmethod
    def get_modules_by_domain() -> Dict[str, List[Dict[str, Any]]]:
        modules = EnterpriseModuleService.get_all_modules()
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for m in modules:
            domain = m["domain_group"]
            if domain not in grouped:
                grouped[domain] = []
            grouped[domain].append(m)
        return grouped

    @staticmethod
    def get_module_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        m = db.query_one(
            "SELECT * FROM enterprise_modules WHERE route_slug = ?",
            (slug,)
        )
        return EnterpriseModuleService._enrich_module(m)

    @staticmethod
    def get_module_records(module_code: str, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT r.*, c.name AS company_name, c.short_code AS company_code_str, c.code AS company_numeric_code
                FROM module_records r
                JOIN companies c ON r.company_id = c.id
                WHERE r.module_code = ? AND r.company_id = ? AND COALESCE(r.isDelete, 0) = 0
                ORDER BY r.created_at DESC, r.code DESC
                """,
                (module_code, company_id)
            )
        return db.query(
            """
            SELECT r.*, c.name AS company_name, c.short_code AS company_code_str, c.code AS company_numeric_code
            FROM module_records r
            JOIN companies c ON r.company_id = c.id
            WHERE r.module_code = ? AND COALESCE(r.isDelete, 0) = 0
            ORDER BY r.created_at DESC, r.code DESC
            """,
            (module_code,)
        )

    @staticmethod
    def get_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT r.*, c.name AS company_name, c.short_code AS company_code_str
            FROM module_records r
            JOIN companies c ON r.company_id = c.id
            WHERE r.id = ? AND COALESCE(r.isDelete, 0) = 0
            """,
            (record_id,)
        )

    @staticmethod
    def add_module_record(
        company_id: str,
        module_code: str,
        record_type: str,
        ref_number: str,
        title: str,
        status: str,
        amount: float,
        party_name: str,
        created_by: str = "Operator Admin"
    ) -> bool:
        db.execute(
            """
            INSERT INTO module_records (company_id, module_code, record_type, ref_number, title, status, amount, party_name, created_by, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (company_id, module_code, record_type, ref_number, title, status, amount, party_name, created_by)
        )
        return True

    @staticmethod
    def update_module_record(
        record_id: str,
        record_type: str,
        title: str,
        status: str,
        amount: float,
        party_name: str
    ) -> bool:
        db.execute(
            """
            UPDATE module_records 
            SET record_type = ?, title = ?, status = ?, amount = ?, party_name = ?
            WHERE id = ?
            """,
            (record_type, title, status, amount, party_name, record_id)
        )
        return True

    @staticmethod
    def delete_record(record_id: str) -> bool:
        try:
            valid_uuid = str(uuid.UUID(str(record_id)))
            db.execute("UPDATE module_records SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (valid_uuid,))
            return True
        except (ValueError, Exception):
            return False
