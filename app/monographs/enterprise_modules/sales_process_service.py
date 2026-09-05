from typing import List, Dict, Any, Optional
from app.core.db import db
from app.monographs.enterprise_modules.sales_transaction_service import SalesTransactionService

class SalesProcessService:

    # =========================================================================
    # 1. VISUAL DOCUMENT FLOW TRACER
    # =========================================================================
    @staticmethod
    def get_document_flow(order_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns document relationship nodes and status progression for visual tracing."""
        if not order_id:
            # Return recent orders flow summary
            orders = db.query(
                """
                SELECT TOP 10 o.id AS order_id, o.order_number, o.customer_name, o.total_amount, o.status,
                       q.quote_number, q.id AS quote_id,
                       do.do_number, do.id AS do_id,
                       inv.invoice_number, inv.id AS invoice_id, inv.gl_journal_ref
                FROM sales_orders o
                LEFT JOIN sales_quotes q ON o.quote_id = q.id
                LEFT JOIN sales_delivery_orders do ON do.order_id = o.id
                LEFT JOIN sales_invoices inv ON inv.order_id = o.id
                ORDER BY o.code DESC
                """
            )
            return orders

        order = SalesTransactionService.get_order_by_id(order_id)
        if not order:
            return []
        
        quote = db.query_one("SELECT * FROM sales_quotes WHERE id = ?", (order.get("quote_id"),)) if order.get("quote_id") else None
        do_list = order.get("delivery_orders", [])
        inv_list = order.get("invoices", [])

        steps = []
        if quote:
            steps.append({"step": 1, "type": "QUOTE", "title": f"Quotation {quote['quote_number']}", "date": str(quote['quote_date']), "status": quote['status'], "amount": quote['total_amount']})
        
        steps.append({"step": 2, "type": "ORDER", "title": f"Sales Order {order['order_number']}", "date": str(order['order_date']), "status": order['status'], "amount": order['total_amount']})

        for do in do_list:
            steps.append({"step": 3, "type": "DO", "title": f"Delivery Order {do['do_number']}", "date": str(do['do_date']), "status": do['status'], "carrier": do.get('carrier_name')})

        for inv in inv_list:
            steps.append({"step": 4, "type": "INVOICE", "title": f"Invoice {inv['invoice_number']}", "date": str(inv['invoice_date']), "status": inv['status'], "amount": inv['total_amount'], "gl_ref": inv.get('gl_journal_ref')})

        return steps

    # =========================================================================
    # 2. DSS (DECISION SUPPORT SYSTEM) MARGIN SIMULATOR
    # =========================================================================
    @staticmethod
    def simulate_order_dss(items: List[Dict[str, Any]], discount_pct: float = 0.0) -> Dict[str, Any]:
        """Calculates expected margin, floor price breach, and discount limits compliance."""
        total_revenue = 0.0
        total_cost = 0.0

        for it in items:
            qty = float(it.get("quantity", 1))
            selling_p = float(it.get("unit_price", 0)) * (1.0 - (discount_pct / 100.0))
            # Production / acquisition cost baseline estimate
            est_cost = selling_p * 0.65
            total_revenue += (selling_p * qty)
            total_cost += (est_cost * qty)

        gross_profit = total_revenue - total_cost
        gross_margin_pct = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

        is_healthy = gross_margin_pct >= 25.0
        requires_director_approval = discount_pct > 15.0 or gross_margin_pct < 20.0

        return {
            "total_revenue": round(total_revenue, 2),
            "estimated_cost": round(total_cost, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 1),
            "is_healthy": is_healthy,
            "requires_director_approval": requires_director_approval,
            "status_label": "HEALTHY_MARGIN" if is_healthy else "LOW_MARGIN_REVIEW"
        }

    # =========================================================================
    # 3. ON-HOLD ORDER MANAGEMENT & MULTI-TIER APPROVALS
    # =========================================================================
    @staticmethod
    def toggle_order_hold(order_id: str, is_hold: bool, reason: Optional[str] = None) -> None:
        db.execute(
            """
            UPDATE sales_orders 
            SET is_on_hold = ?, hold_reason = ?, status = CASE WHEN ? = 1 THEN 'ON_HOLD' ELSE 'APPROVED' END
            WHERE id = ?
            """,
            (1 if is_hold else 0, reason if is_hold else None, 1 if is_hold else 0, order_id)
        )

    @staticmethod
    def approve_order_tier(order_id: str, approver_name: str, approver_role: str, comments: str = "Approved") -> None:
        order = db.query_one("SELECT current_approval_tier, max_approval_tier FROM sales_orders WHERE id = ?", (order_id,))
        if not order:
            return
        
        curr_tier = order["current_approval_tier"]
        max_tier = order["max_approval_tier"]

        db.execute(
            """
            INSERT INTO sales_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments, action_date)
            VALUES ('SO', ?, ?, ?, ?, ?, 'APPROVED', ?, GETDATE())
            """,
            (order_id, curr_tier, f"Tier {curr_tier} Validation", approver_name, approver_role, comments)
        )

        next_tier = curr_tier + 1
        if next_tier > max_tier:
            db.execute("UPDATE sales_orders SET status = 'APPROVED', current_approval_tier = ? WHERE id = ?", (max_tier, order_id))
        else:
            db.execute("UPDATE sales_orders SET current_approval_tier = ? WHERE id = ?", (next_tier, order_id))
