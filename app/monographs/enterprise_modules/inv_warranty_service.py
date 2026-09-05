from typing import List, Dict, Any, Optional
from app.core.db import db

class InvWarrantyService:

    # =========================================================================
    # 1. SERIAL NUMBER & WARRANTY REGISTRY
    # =========================================================================
    @staticmethod
    def get_warranties(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT w.*, it.item_code, it.item_name, it.specification, c.short_code AS company_code
        FROM inv_warranties w
        JOIN companies c ON w.company_id = c.id
        JOIN inv_items it ON w.item_id = it.id
        """
        params = ()
        if company_id:
            sql += " WHERE w.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY w.code DESC"
        return db.query(sql, params)

    # =========================================================================
    # 2. BARCODE & SERIAL PRODUCT INQUIRY SCANNER
    # =========================================================================
    @staticmethod
    def search_by_serial(serial_number: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT w.*, it.item_code, it.item_name, it.specification, it.uom_code,
                   c.name AS company_name, c.short_code AS company_code
            FROM inv_warranties w
            JOIN companies c ON w.company_id = c.id
            JOIN inv_items it ON w.item_id = it.id
            WHERE w.serial_number = ?
            """,
            (serial_number.strip(),)
        )
