from typing import List, Dict, Any, Optional
from app.core.db import db

class FAVerificationService:

    @staticmethod
    def get_physical_audits(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT pa.*, l.location_name, l.location_code, c.short_code AS company_code
        FROM fa_physical_audits pa
        JOIN fa_locations l ON pa.location_id = l.id
        JOIN companies c ON pa.company_id = c.id
        """
        params = ()
        if company_id:
            sql += " WHERE pa.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY pa.code DESC"
        return db.query(sql, params)

    @staticmethod
    def scan_asset_inquiry(query: str, company_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Instant lookup by barcode, tag #, or serial number."""
        sql = """
        SELECT a.*, g.group_name, l.location_name, l.address AS location_address,
               sub.sub_location_name, p.policy_name, p.method AS depr_method,
               c.name AS company_name, c.currency
        FROM fa_assets a
        JOIN fa_asset_groups g ON a.group_id = g.id
        JOIN fa_locations l ON a.location_id = l.id
        LEFT JOIN fa_sub_locations sub ON a.sub_location_id = sub.id
        JOIN fa_depreciation_policies p ON a.policy_id = p.id
        JOIN companies c ON a.company_id = c.id
        WHERE (a.barcode = ? OR a.asset_tag = ? OR a.serial_number = ?)
        """
        params = [query, query, query]
        if company_id:
            sql += " AND a.company_id = ?"
            params.append(company_id)
        return db.query_one(sql, tuple(params))
