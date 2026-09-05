from typing import List, Dict, Any, Optional
from app.core.db import db

class FAAssetService:

    @staticmethod
    def get_assets(company_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT a.*, g.group_name, g.group_code, g.asset_type, g.is_depreciating,
               l.location_name, l.location_code,
               sub.sub_location_name, sub.floor_or_bay,
               p.policy_name, p.method AS depr_method, p.depr_rate,
               c.short_code AS company_code, c.currency
        FROM fa_assets a
        JOIN fa_asset_groups g ON a.group_id = g.id
        JOIN fa_locations l ON a.location_id = l.id
        LEFT JOIN fa_sub_locations sub ON a.sub_location_id = sub.id
        JOIN fa_depreciation_policies p ON a.policy_id = p.id
        JOIN companies c ON a.company_id = c.id
        WHERE a.is_active = 1
        """
        params = []
        if company_id:
            sql += " AND a.company_id = ?"
            params.append(company_id)
        if status:
            sql += " AND a.status = ?"
            params.append(status)
        sql += " ORDER BY a.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT a.*, g.group_name, g.group_code, g.asset_type, g.is_depreciating,
               l.location_name, l.location_code, l.address AS location_address,
               sub.sub_location_name, sub.floor_or_bay,
               p.policy_name, p.method AS depr_method, p.depr_rate, p.useful_life_years, p.salvage_value_pct,
               c.name AS company_name, c.short_code AS company_code, c.currency
        FROM fa_assets a
        JOIN fa_asset_groups g ON a.group_id = g.id
        JOIN fa_locations l ON a.location_id = l.id
        LEFT JOIN fa_sub_locations sub ON a.sub_location_id = sub.id
        JOIN fa_depreciation_policies p ON a.policy_id = p.id
        JOIN companies c ON a.company_id = c.id
        WHERE a.id = ?
        """
        return db.query_one(sql, (asset_id,))

    @staticmethod
    def get_asset_grns(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT grn.*, l.location_name, l.location_code, c.short_code AS company_code
        FROM fa_grn_headers grn
        JOIN fa_locations l ON grn.location_id = l.id
        JOIN companies c ON grn.company_id = c.id
        """
        params = ()
        if company_id:
            sql += " WHERE grn.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY grn.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_transfers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT t.*, a.asset_tag, a.asset_name,
               lf.location_name AS from_location_name, lt.location_name AS to_location_name,
               c.short_code AS company_code
        FROM fa_transfers t
        JOIN fa_assets a ON t.asset_id = a.id
        JOIN fa_locations lf ON t.from_location_id = lf.id
        JOIN fa_locations lt ON t.to_location_id = lt.id
        JOIN companies c ON t.company_id = c.id
        """
        params = ()
        if company_id:
            sql += " WHERE t.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY t.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_disposals(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT d.*, a.asset_tag, a.asset_name, c.short_code AS company_code
        FROM fa_disposals d
        JOIN fa_assets a ON d.asset_id = a.id
        JOIN companies c ON d.company_id = c.id
        """
        params = ()
        if company_id:
            sql += " WHERE d.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY d.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_spares_mapping(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Maps inventory spare parts to capital machinery."""
        sql = """
        SELECT a.asset_tag, a.asset_name, a.manufacturer, a.model_number,
               i.item_code AS spare_part_code, i.item_name AS spare_part_name,
               i.uom_code, i.standard_cost AS spare_cost,
               ISNULL(sb.on_hand_qty, 0) AS spare_stock_on_hand,
               l.location_name
        FROM fa_assets a
        JOIN fa_locations l ON a.location_id = l.id
        LEFT JOIN inv_items i ON i.group_id IN (SELECT id FROM inv_product_groups WHERE group_type = 'SPARE_PARTS')
        LEFT JOIN inv_stock_balances sb ON sb.item_id = i.id
        WHERE a.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND a.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY a.code DESC"
        return db.query(sql, params)
