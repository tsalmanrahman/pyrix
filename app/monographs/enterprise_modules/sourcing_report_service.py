from typing import List, Dict, Any, Optional
from app.core.db import db

class SourcingReportService:

    # =========================================================================
    # 1. PR vs PO vs GRN 3-WAY RECONCILIATION AUDIT ENGINE
    # =========================================================================
    @staticmethod
    def get_three_way_reconciliation_matrix(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT po.id AS po_id, po.po_number, po.po_category, po.total_amount, po.currency, po.status AS po_status,
                   c.short_code AS company_code,
                   v.vendor_code, v.vendor_name,
                   r.req_number, r.req_type, r.total_estimated_amount AS pr_estimated_total,
                   pi.item_code, pi.item_name, pi.uom, pi.quantity AS po_ordered_qty, pi.unit_price AS po_unit_price, pi.line_total AS po_line_total, pi.received_qty,
                   ri.quantity AS pr_requested_qty, ri.estimated_unit_price AS pr_estimated_price,
                   lc.lc_number, lc.status AS lc_status
            FROM sourcing_po_items pi
            JOIN sourcing_purchase_orders po ON pi.po_id = po.id
            JOIN companies c ON po.company_id = c.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            LEFT JOIN sourcing_requisitions r ON po.requisition_id = r.id
            LEFT JOIN sourcing_requisition_items ri ON (r.id = ri.requisition_id AND pi.item_code = ri.item_code)
            LEFT JOIN sourcing_letters_of_credit lc ON po.id = lc.po_id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY po.code DESC, pi.code ASC"

        raw_rows = db.query(sql, tuple(params) if params else ())
        matrix = []
        for r in raw_rows:
            po_qty = float(r.get("po_ordered_qty") or 0)
            rec_qty = float(r.get("received_qty") or 0)
            pr_qty = float(r.get("pr_requested_qty") or po_qty)

            # Determine reconciliation state
            if rec_qty >= po_qty and po_qty > 0:
                match_status = "100% MATCHED"
                badge_color = "emerald"
            elif rec_qty > 0 and rec_qty < po_qty:
                match_status = "PARTIAL RECEIPT"
                badge_color = "amber"
            else:
                match_status = "AWAITING DELIVERY"
                badge_color = "blue"

            r["match_status"] = match_status
            r["badge_color"] = badge_color
            matrix.append(r)

        return matrix

    # =========================================================================
    # 2. PURCHASE REGISTERS (PERIOD & TAX AUDIT)
    # =========================================================================
    @staticmethod
    def get_purchase_register(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT po.po_number, po.created_at AS po_date, po.po_category, po.currency,
                   po.subtotal, po.tax_amount, po.freight_amount, po.total_amount, po.status,
                   c.short_code AS company_code, c.name AS company_name,
                   v.vendor_code, v.vendor_name, v.tax_id_tin, v.vat_bin
            FROM sourcing_purchase_orders po
            JOIN companies c ON po.company_id = c.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY po.code DESC"
        return db.query(sql, tuple(params) if params else ())

    # =========================================================================
    # 3. LC MATURITY & SETTLEMENT SCHEDULE
    # =========================================================================
    @staticmethod
    def get_lc_maturity_schedule() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT lc.*, po.po_number, v.vendor_name, v.vendor_code
            FROM sourcing_letters_of_credit lc
            JOIN sourcing_purchase_orders po ON lc.po_id = po.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            ORDER BY lc.expiry_date ASC
            """
        )
