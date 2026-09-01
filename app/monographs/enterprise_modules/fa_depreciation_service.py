from typing import List, Dict, Any, Optional
from app.core.db import db

class FADepreciationService:

    @staticmethod
    def get_depreciation_runs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT r.*, c.short_code AS company_code
        FROM fa_depreciation_runs r
        JOIN companies c ON r.company_id = c.id
        """
        params = ()
        if company_id:
            sql += " WHERE r.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY r.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_depreciation_lines(run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT dl.*, a.asset_tag, a.asset_name, g.group_name, l.location_name
        FROM fa_depreciation_lines dl
        JOIN fa_assets a ON dl.asset_id = a.id
        JOIN fa_asset_groups g ON a.group_id = g.id
        JOIN fa_locations l ON a.location_id = l.id
        """
        params = ()
        if run_id:
            sql += " WHERE dl.run_id = ?"
            params = (run_id,)
        sql += " ORDER BY dl.code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_depreciation_simulation(company_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates live monthly & annual depreciation across all active depreciating assets."""
        assets = db.query(
            """
            SELECT a.id, a.asset_tag, a.asset_name, a.purchase_cost, a.accumulated_depreciation, a.net_book_value,
                   g.group_name, g.is_depreciating, p.method, p.depr_rate, p.useful_life_years, p.salvage_value_pct,
                   l.location_name, a.department_name
            FROM fa_assets a
            JOIN fa_asset_groups g ON a.group_id = g.id
            JOIN fa_depreciation_policies p ON a.policy_id = p.id
            JOIN fa_locations l ON a.location_id = l.id
            WHERE a.is_active = 1 AND g.is_depreciating = 1 AND a.status = 'IN_SERVICE'
            """
        )
        simulated_lines = []
        total_monthly_depr = 0.0
        total_annual_depr = 0.0

        for a in assets:
            cost = float(a["purchase_cost"])
            salvage_pct = float(a.get("salvage_value_pct", 5.0))
            salvage_val = cost * (salvage_pct / 100.0)
            depreciable_base = cost - salvage_val
            rate = float(a.get("depr_rate", 10.0))
            method = a.get("method", "STRAIGHT_LINE")

            if method == "STRAIGHT_LINE":
                annual_depr = depreciable_base * (rate / 100.0)
            elif method == "REDUCING_BALANCE_WDV":
                nbv = float(a["net_book_value"])
                annual_depr = nbv * (rate / 100.0)
            else:
                annual_depr = 0.0

            monthly_depr = annual_depr / 12.0
            total_monthly_depr += monthly_depr
            total_annual_depr += annual_depr

            simulated_lines.append({
                "asset_tag": a["asset_tag"],
                "asset_name": a["asset_name"],
                "group_name": a["group_name"],
                "location_name": a["location_name"],
                "method": method,
                "cost": cost,
                "accumulated_depr": float(a["accumulated_depreciation"]),
                "current_nbv": float(a["net_book_value"]),
                "monthly_depr": monthly_depr,
                "annual_depr": annual_depr,
                "projected_nbv": max(0.0, float(a["net_book_value"]) - monthly_depr)
            })

        return {
            "lines": simulated_lines,
            "total_monthly_depr": total_monthly_depr,
            "total_annual_depr": total_annual_depr,
            "eligible_assets_count": len(simulated_lines),
            "gl_batch_status": "READY TO POST AUTOMATED GL JOURNALS"
        }

    @staticmethod
    def get_approvals(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT ap.*
        FROM fa_approvals ap
        ORDER BY ap.code DESC
        """
        return db.query(sql)
