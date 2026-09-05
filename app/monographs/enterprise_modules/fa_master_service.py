from typing import List, Dict, Any, Optional
from app.core.db import db

class FAMasterService:

    @staticmethod
    def get_asset_groups(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT g.*, c.short_code AS company_code,
               (SELECT COUNT(*) FROM fa_assets a WHERE a.group_id = g.id AND a.is_active = 1) AS active_asset_count,
               (SELECT ISNULL(SUM(a.purchase_cost), 0) FROM fa_assets a WHERE a.group_id = g.id AND a.is_active = 1) AS total_gross_cost
        FROM fa_asset_groups g
        JOIN companies c ON g.company_id = c.id
        WHERE g.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND g.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY g.code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_locations(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT l.*, c.short_code AS company_code,
               (SELECT COUNT(*) FROM fa_sub_locations s WHERE s.location_id = l.id) AS sub_location_count,
               (SELECT COUNT(*) FROM fa_assets a WHERE a.location_id = l.id AND a.is_active = 1) AS deployed_asset_count
        FROM fa_locations l
        JOIN companies c ON l.company_id = c.id
        WHERE l.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND l.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY l.code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_sub_locations(location_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT s.*, l.location_name, l.location_code
        FROM fa_sub_locations s
        JOIN fa_locations l ON s.location_id = l.id
        WHERE s.is_active = 1
        """
        params = ()
        if location_id:
            sql += " AND s.location_id = ?"
            params = (location_id,)
        sql += " ORDER BY s.code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_depreciation_policies(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT p.*, c.short_code AS company_code,
               (SELECT COUNT(*) FROM fa_assets a WHERE a.policy_id = p.id AND a.is_active = 1) AS applied_asset_count
        FROM fa_depreciation_policies p
        JOIN companies c ON p.company_id = c.id
        WHERE p.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND p.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY p.code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_gl_control_sets(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT g.group_code, g.group_name, g.gl_cost_account, g.gl_acc_depr_account,
               g.gl_depr_expense_account, g.gl_gain_loss_account, c.short_code AS company_code
        FROM fa_asset_groups g
        JOIN companies c ON g.company_id = c.id
        WHERE g.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND g.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY g.code ASC"
        return db.query(sql, params)
