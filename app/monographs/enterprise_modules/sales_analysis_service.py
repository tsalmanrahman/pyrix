from typing import List, Dict, Any, Optional
from app.core.db import db

class SalesAnalysisService:

    # =========================================================================
    # 1. MULTI-DIMENSIONAL PIVOT: SALES, COLLECTION & AR
    # =========================================================================
    @staticmethod
    def get_sales_collection_pivot(company_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns monthly and annual pivots comparing Billed Sales, Collections & AR Balance."""
        sales_by_month = db.query(
            """
            SELECT FORMAT(invoice_date, 'yyyy-MM') AS [month_key],
                   DATENAME(month, invoice_date) AS [month_name],
                   SUM(total_amount) AS billed_sales,
                   SUM(paid_amount) AS collected_amount,
                   SUM(total_amount - paid_amount) AS outstanding_amount
            FROM sales_invoices
            GROUP BY FORMAT(invoice_date, 'yyyy-MM'), DATENAME(month, invoice_date)
            ORDER BY [month_key] DESC
            """
        )

        total_billed = sum(m["billed_sales"] for m in sales_by_month)
        total_collected = sum(m["collected_amount"] for m in sales_by_month)
        total_ar = sum(m["outstanding_amount"] for m in sales_by_month)

        return {
            "monthly_data": sales_by_month,
            "total_billed": round(total_billed, 2),
            "total_collected": round(total_collected, 2),
            "total_ar": round(total_ar, 2),
            "collection_efficiency_pct": round((total_collected / total_billed * 100.0) if total_billed > 0 else 100.0, 1)
        }

    # =========================================================================
    # 2. HIERARCHICAL DRILLDOWN: MM > ZM > TSM WISE BUDGET & SALES
    # =========================================================================
    @staticmethod
    def get_hierarchical_performance(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns performance matrix categorized by Sales Management Hierarchy."""
        sql = """
        SELECT t.team_name, t.team_type, t.manager_name, t.target_annual_amount,
               ISNULL(SUM(o.total_amount), 0) AS achieved_sales,
               c.short_code AS company_code
        FROM sales_teams t
        JOIN companies c ON t.company_id = c.id
        LEFT JOIN salespersons sp ON sp.team_id = t.id
        LEFT JOIN sales_orders o ON o.salesperson_id = sp.id AND o.status != 'CANCELLED'
        """
        params = ()
        if company_id:
            sql += " WHERE t.company_id = ?"
            params = (company_id,)
        sql += " GROUP BY t.team_name, t.team_type, t.manager_name, t.target_annual_amount, c.short_code ORDER BY t.team_type ASC, achieved_sales DESC"
        
        rows = db.query(sql, params)
        for r in rows:
            tgt = r.get("target_annual_amount", 0) or 1
            ach = r.get("achieved_sales", 0)
            r["achievement_pct"] = round((ach / tgt * 100.0), 1)
        return rows

    # =========================================================================
    # 3. SALES TARGET VS ACHIEVEMENT VARIANCE
    # =========================================================================
    @staticmethod
    def get_target_vs_achievement(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, sp.full_name AS salesperson_name, sp.salesperson_code, c.short_code AS company_code,
                   ROUND((b.achieved_amount / NULLIF(b.annual_target, 0) * 100.0), 1) AS progress_pct,
                   (b.annual_target - b.achieved_amount) AS variance_amount
            FROM sales_budgets b
            JOIN companies c ON b.company_id = c.id
            LEFT JOIN salespersons sp ON b.salesperson_id = sp.id
            ORDER BY b.code ASC
            """
        )
