from typing import List, Dict, Any, Optional
from app.core.db import db

class SalesReportService:

    # =========================================================================
    # 1. DO - GI - INVOICE PENDING RECONCILIATION
    # =========================================================================
    @staticmethod
    def get_do_invoice_pending_report(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identifies delivery orders dispatched that have not yet been fully invoiced."""
        return db.query(
            """
            SELECT do.do_number, do.do_date, do.dispatch_date, do.carrier_name,
                   so.order_number, so.customer_name, so.total_amount AS order_value,
                   c.short_code AS company_code,
                   inv.invoice_number, inv.status AS invoice_status,
                   CASE WHEN inv.id IS NULL THEN 'UNINVOICED' ELSE 'INVOICED' END AS reconciliation_status
            FROM sales_delivery_orders do
            JOIN companies c ON do.company_id = c.id
            JOIN sales_orders so ON do.order_id = so.id
            LEFT JOIN sales_invoices inv ON inv.do_id = do.id
            ORDER BY do.code DESC
            """
        )

    # =========================================================================
    # 2. CONSOLIDATED SALES & OUTSTANDING STATEMENT
    # =========================================================================
    @staticmethod
    def get_consolidated_statement(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT c.name AS company_name, c.short_code,
                   COUNT(DISTINCT so.id) AS total_orders_count,
                   ISNULL(SUM(so.total_amount), 0) AS total_ordered_amount,
                   COUNT(DISTINCT inv.id) AS total_invoices_count,
                   ISNULL(SUM(inv.total_amount), 0) AS total_invoiced_amount,
                   ISNULL(SUM(inv.paid_amount), 0) AS total_collected_amount,
                   ISNULL(SUM(inv.total_amount - inv.paid_amount), 0) AS net_outstanding_amount
            FROM companies c
            LEFT JOIN sales_orders so ON so.company_id = c.id AND so.status != 'CANCELLED'
            LEFT JOIN sales_invoices inv ON inv.company_id = c.id
            GROUP BY c.name, c.short_code, c.sort_order
            ORDER BY c.sort_order ASC
            """
        )

    # =========================================================================
    # 3. PROFITABILITY & DISCOUNT AUDIT REPORT
    # =========================================================================
    @staticmethod
    def get_profitability_report(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT oi.item_code, oi.item_name, oi.uom,
                   SUM(oi.quantity) AS total_sold_qty,
                   AVG(oi.unit_price) AS avg_selling_price,
                   AVG(oi.discount_pct) AS avg_discount_pct,
                   SUM(oi.line_total) AS total_revenue,
                   ROUND(SUM(oi.line_total) * 0.65, 2) AS estimated_production_cost,
                   ROUND(SUM(oi.line_total) * 0.35, 2) AS gross_profit_margin,
                   35.0 AS margin_pct
            FROM sales_order_items oi
            JOIN sales_orders so ON oi.order_id = so.id
            WHERE so.status != 'CANCELLED'
            GROUP BY oi.item_code, oi.item_name, oi.uom
            ORDER BY total_revenue DESC
            """
        )
