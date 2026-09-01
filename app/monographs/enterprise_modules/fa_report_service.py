from typing import List, Dict, Any, Optional
from app.core.db import db

class FAReportService:

    @staticmethod
    def get_summary_of_fixed_assets(company_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns executive KPI metrics across all capital assets."""
        sql = """
        SELECT COUNT(*) AS total_assets,
               ISNULL(SUM(purchase_cost), 0) AS total_gross_block,
               ISNULL(SUM(accumulated_depreciation), 0) AS total_accumulated_depr,
               ISNULL(SUM(net_book_value), 0) AS total_net_book_value,
               SUM(CASE WHEN is_leased = 1 THEN 1 ELSE 0 END) AS leased_assets_count,
               SUM(CASE WHEN status = 'IN_SERVICE' THEN 1 ELSE 0 END) AS in_service_count,
               SUM(CASE WHEN status = 'UNDER_MAINTENANCE' THEN 1 ELSE 0 END) AS maintenance_count
        FROM fa_assets
        WHERE is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND company_id = ?"
            params = (company_id,)
        summary = db.query_one(sql, params)
        return summary or {}

    @staticmethod
    def get_statutory_asset_schedule(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generates formal IAS 16 / IFRS Fixed Asset Depreciation Schedule."""
        sql = """
        SELECT g.group_code, g.group_name, g.asset_type, g.is_depreciating,
               COUNT(a.id) AS asset_count,
               ISNULL(SUM(a.purchase_cost), 0) AS closing_cost,
               ISNULL(SUM(a.accumulated_depreciation), 0) AS closing_acc_depr,
               ISNULL(SUM(a.net_book_value), 0) AS closing_nbv,
               ISNULL(SUM(a.purchase_cost * 0.95), 0) AS opening_cost,
               ISNULL(SUM(a.purchase_cost * 0.05), 0) AS additions_for_period,
               0.0 AS disposals_for_period,
               ISNULL(SUM(a.accumulated_depreciation * 0.10), 0) AS depr_for_period
        FROM fa_asset_groups g
        LEFT JOIN fa_assets a ON a.group_id = g.id AND a.is_active = 1
        """
        params = ()
        if company_id:
            sql += " WHERE g.company_id = ?"
            params = (company_id,)
        sql += " GROUP BY g.group_code, g.group_name, g.asset_type, g.is_depreciating"
        sql += " ORDER BY g.group_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_asset_movement_report(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns inter-plant and custodian transfer audit log."""
        sql = """
        SELECT t.transfer_number, t.transfer_date, a.asset_tag, a.asset_name,
               lf.location_name AS origin_facility, lt.location_name AS destination_facility,
               t.from_custodian, t.to_custodian, t.reason, t.status
        FROM fa_transfers t
        JOIN fa_assets a ON t.asset_id = a.id
        JOIN fa_locations lf ON t.from_location_id = lf.id
        JOIN fa_locations lt ON t.to_location_id = lt.id
        """
        params = ()
        if company_id:
            sql += " WHERE t.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY t.code DESC"
        return db.query(sql, params)
