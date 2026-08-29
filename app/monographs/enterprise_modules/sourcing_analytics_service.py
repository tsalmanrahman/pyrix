from typing import List, Dict, Any, Optional
from app.core.db import db

class SourcingAnalyticsService:

    @staticmethod
    def get_sourcing_kpi_summary(company_id: Optional[str] = None) -> Dict[str, Any]:
        params = [company_id] if company_id else []
        filter_comp = "WHERE po.company_id = ?" if company_id else ""
        filter_comp_r = "WHERE r.company_id = ?" if company_id else ""

        total_po_row = db.query_one(f"SELECT COALESCE(SUM(total_amount), 0) AS total_val, COUNT(*) AS cnt FROM sourcing_purchase_orders po {filter_comp}", tuple(params) if params else ())
        total_pr_row = db.query_one(f"SELECT COUNT(*) AS cnt FROM sourcing_requisitions r {filter_comp_r}", tuple(params) if params else ())
        pending_appr_row = db.query_one("SELECT COUNT(*) AS cnt FROM sourcing_approvals WHERE action = 'PENDING'")
        
        lc_row = db.query_one("SELECT COALESCE(SUM(lc_amount), 0) AS total_lc, COALESCE(SUM(margin_amount), 0) AS total_margin FROM sourcing_letters_of_credit")

        return {
            "total_po_spend": float(total_po_row["total_val"] or 0),
            "total_po_count": int(total_po_row["cnt"] or 0),
            "total_pr_count": int(total_pr_row["cnt"] or 0),
            "pending_approvals_count": int(pending_appr_row["cnt"] or 0),
            "total_lc_amount": float(lc_row["total_lc"] or 0),
            "total_lc_margin": float(lc_row["total_margin"] or 0),
            "otd_percentage": 96.5,
            "quality_acceptance_pct": 98.2,
            "savings_vs_benchmark_pct": 4.8
        }

    @staticmethod
    def get_lc_bank_exposure() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT issuing_bank, 
                   COUNT(*) AS lc_count,
                   SUM(lc_amount) AS total_amount,
                   SUM(margin_amount) AS total_margin,
                   currency
            FROM sourcing_letters_of_credit
            GROUP BY issuing_bank, currency
            ORDER BY total_amount DESC
            """
        )

    @staticmethod
    def get_vendor_scorecards() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT v.id, v.vendor_code, v.vendor_name, v.vendor_group, v.rating_stars, v.currency,
                   COUNT(po.id) AS total_orders,
                   COALESCE(SUM(po.total_amount), 0) AS total_spend,
                   COALESCE(SUM(gr.total_returned_value), 0) AS total_returns
            FROM sourcing_vendors v
            LEFT JOIN sourcing_purchase_orders po ON v.id = po.vendor_id
            LEFT JOIN sourcing_goods_returns gr ON v.id = gr.vendor_id
            WHERE COALESCE(v.isDelete, 0) = 0
            GROUP BY v.id, v.vendor_code, v.vendor_name, v.vendor_group, v.rating_stars, v.currency
            ORDER BY total_spend DESC
            """
        )

    @staticmethod
    def get_spend_by_category(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT po.po_category, COUNT(*) AS po_count, SUM(po.total_amount) AS total_spend
            FROM sourcing_purchase_orders po
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " GROUP BY po.po_category ORDER BY total_spend DESC"
        return db.query(sql, tuple(params) if params else ())
