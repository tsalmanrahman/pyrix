import uuid
import datetime
from typing import Optional, List, Dict, Any
from app.core.db import db

class APMasterService:
    @staticmethod
    def get_control_account_sets(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT s.*,
                   c.name AS company_name,
                   ap_gl.account_number AS ap_gl_number, ap_gl.account_name AS ap_gl_name,
                   pur_gl.account_number AS purchase_gl_number, pur_gl.account_name AS purchase_gl_name,
                   adv_gl.account_number AS advance_gl_number, adv_gl.account_name AS advance_gl_name,
                   vat_gl.account_number AS vat_gl_number, vat_gl.account_name AS vat_gl_name,
                   ait_gl.account_number AS ait_gl_number, ait_gl.account_name AS ait_gl_name
            FROM ap_control_account_sets s
            LEFT JOIN companies c ON s.company_id = c.id
            LEFT JOIN gl_accounts ap_gl ON s.accounts_payable_gl_id = ap_gl.id
            LEFT JOIN gl_accounts pur_gl ON s.purchase_gl_id = pur_gl.id
            LEFT JOIN gl_accounts adv_gl ON s.advance_to_vendors_gl_id = adv_gl.id
            LEFT JOIN gl_accounts vat_gl ON s.vat_on_purchase_gl_id = vat_gl.id
            LEFT JOIN gl_accounts ait_gl ON s.advance_income_tax_gl_id = ait_gl.id
            WHERE s.company_id = ? AND COALESCE(s.isDelete, 0) = 0
            ORDER BY s.code ASC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_control_account_set_by_id(set_id: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM ap_control_account_sets WHERE id = ?"
        return db.query_one(sql, (set_id,))

    @staticmethod
    def save_control_account_set(data: Dict[str, Any]) -> str:
        set_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM ap_control_account_sets WHERE id = ?", (set_id,))
        if existing:
            sql = """
                UPDATE ap_control_account_sets SET
                    set_code = ?, set_name = ?,
                    accounts_payable_gl_id = ?, purchase_gl_id = ?,
                    advance_to_vendors_gl_id = ?, special_purchase_discount_gl_id = ?,
                    ap_adjustment_gl_id = ?, vat_on_purchase_gl_id = ?,
                    advance_income_tax_gl_id = ?, bad_ap_gl_id = ?,
                    tax_others_gl_id = ?, freight_gl_id = ?,
                    design_consultants_fees_gl_id = ?, is_active = ?
                WHERE id = ?
            """
            db.execute(sql, (
                data.get("set_code"), data.get("set_name"),
                data.get("accounts_payable_gl_id"), data.get("purchase_gl_id"),
                data.get("advance_to_vendors_gl_id"), data.get("special_purchase_discount_gl_id"),
                data.get("ap_adjustment_gl_id"), data.get("vat_on_purchase_gl_id"),
                data.get("advance_income_tax_gl_id"), data.get("bad_ap_gl_id"),
                data.get("tax_others_gl_id"), data.get("freight_gl_id"),
                data.get("design_consultants_fees_gl_id"), 1 if data.get("is_active", True) else 0,
                set_id
            ))
        else:
            sql = """
                INSERT INTO ap_control_account_sets (
                    id, set_code, set_name, company_id,
                    accounts_payable_gl_id, purchase_gl_id,
                    advance_to_vendors_gl_id, special_purchase_discount_gl_id,
                    ap_adjustment_gl_id, vat_on_purchase_gl_id,
                    advance_income_tax_gl_id, bad_ap_gl_id,
                    tax_others_gl_id, freight_gl_id,
                    design_consultants_fees_gl_id, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            db.execute(sql, (
                set_id, data.get("set_code"), data.get("set_name"), data.get("company_id"),
                data.get("accounts_payable_gl_id"), data.get("purchase_gl_id"),
                data.get("advance_to_vendors_gl_id"), data.get("special_purchase_discount_gl_id"),
                data.get("ap_adjustment_gl_id"), data.get("vat_on_purchase_gl_id"),
                data.get("advance_income_tax_gl_id"), data.get("bad_ap_gl_id"),
                data.get("tax_others_gl_id"), data.get("freight_gl_id"),
                data.get("design_consultants_fees_gl_id"), 1 if data.get("is_active", True) else 0
            ))
        return set_id

    @staticmethod
    def get_payment_terms() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM sourcing_price_terms WHERE COALESCE(is_active, 1) = 1 ORDER BY credit_days ASC")

    @staticmethod
    def save_payment_term(data: Dict[str, Any]) -> str:
        term_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM sourcing_price_terms WHERE id = ?", (term_id,))
        if existing:
            db.execute("""
                UPDATE sourcing_price_terms SET
                    term_code = ?, term_name = ?, incoterm = ?,
                    credit_days = ?, validity_period_months = ?,
                    description = ?, is_active = ?
                WHERE id = ?
            """, (
                data.get("term_code"), data.get("term_name"), data.get("incoterm", "DDP"),
                int(data.get("credit_days", 30)), int(data.get("validity_period_months", 12)),
                data.get("description", ""), 1 if data.get("is_active", True) else 0,
                term_id
            ))
        else:
            db.execute("""
                INSERT INTO sourcing_price_terms (id, term_code, term_name, incoterm, credit_days, validity_period_months, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                term_id, data.get("term_code"), data.get("term_name"), data.get("incoterm", "DDP"),
                int(data.get("credit_days", 30)), int(data.get("validity_period_months", 12)),
                data.get("description", ""), 1 if data.get("is_active", True) else 0
            ))
        return term_id

    @staticmethod
    def get_vendor_company_mappings(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT m.*, v.vendor_code, v.vendor_name, v.vendor_group, v.currency, v.credit_terms_days,
                   c.name AS company_name, c.short_code AS company_code
            FROM sourcing_vendor_company_mappings m
            JOIN sourcing_vendors v ON m.vendor_id = v.id
            JOIN companies c ON m.company_id = c.id
            WHERE m.company_id = ?
            ORDER BY v.vendor_code ASC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def save_vendor_company_mapping(data: Dict[str, Any]) -> str:
        map_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM sourcing_vendor_company_mappings WHERE id = ?", (map_id,))
        if existing:
            db.execute("""
                UPDATE sourcing_vendor_company_mappings SET
                    vendor_account_alias = ?, payment_method = ?, is_approved = ?, credit_limit = ?
                WHERE id = ?
            """, (
                data.get("vendor_account_alias"), data.get("payment_method", "BEFTN"),
                1 if data.get("is_approved", True) else 0, float(data.get("credit_limit") or 1000000.0),
                map_id
            ))
        else:
            db.execute("""
                INSERT INTO sourcing_vendor_company_mappings (id, vendor_id, company_id, vendor_account_alias, payment_method, is_approved, credit_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                map_id, data.get("vendor_id"), data.get("company_id"), data.get("vendor_account_alias"),
                data.get("payment_method", "BEFTN"), 1 if data.get("is_approved", True) else 0,
                float(data.get("credit_limit") or 1000000.0)
            ))
        return map_id


class APTransactionService:
    @staticmethod
    def get_purchase_bills(company_id: str, category: Optional[str] = None, bill_type: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT b.*,
                   COALESCE(b.entry_date, b.effective_invoice_date) AS bill_date,
                   COALESCE(b.gross_amount, 0.0) AS subtotal_amount,
                   COALESCE(b.owing_balance, b.net_payable_amount) AS outstanding_amount,
                   b.gross_amount AS gross_amount_val,
                   v.vendor_code, v.vendor_name, v.contact_person, v.email, v.currency AS vendor_currency
            FROM ap_purchase_bills b
            JOIN sourcing_vendors v ON b.vendor_id = v.id
            WHERE b.company_id = ? AND COALESCE(b.isDelete, 0) = 0
        """
        params = [company_id]
        cat = category or bill_type
        if cat:
            sql += " AND (b.bill_category = ? OR b.bill_category LIKE ?)"
            params.extend([cat, f"%{cat}%"])
        sql += " ORDER BY b.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_purchase_bill_by_id(bill_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT b.*,
                   COALESCE(b.entry_date, b.effective_invoice_date) AS bill_date,
                   COALESCE(b.gross_amount, 0.0) AS subtotal_amount,
                   COALESCE(b.owing_balance, b.net_payable_amount) AS outstanding_amount,
                   v.vendor_code, v.vendor_name, v.address AS vendor_address, v.tax_id_tin AS tax_id_tin
            FROM ap_purchase_bills b
            JOIN sourcing_vendors v ON b.vendor_id = v.id
            WHERE b.id = ?
        """
        return db.query_one(sql, (bill_id,))

    @staticmethod
    def get_purchase_bill_grn_lines(bill_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM ap_purchase_bill_grn_lines WHERE bill_id = ? ORDER BY grn_number ASC"
        return db.query(sql, (bill_id,))

    @staticmethod
    def save_purchase_bill(data: Dict[str, Any], grn_lines: Optional[List[Dict[str, Any]]] = None) -> str:
        bill_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM ap_purchase_bills WHERE id = ?", (bill_id,))

        gross = float(data.get("gross_amount") or data.get("subtotal_amount") or 0.0)
        discount = float(data.get("discount_amount") or 0.0)
        adv_adj = float(data.get("advance_adjusted_amount") or data.get("adjusted_advance_amount") or 0.0)
        vat = float(data.get("vat_amount") or 0.0)
        ait = float(data.get("ait_amount") or 0.0)
        retention = float(data.get("security_deposit_amount") or 0.0)
        freight = float(data.get("freight_amount") or 0.0)
        other_tax = float(data.get("other_tax_amount") or 0.0)

        net_payable = float(data.get("net_payable_amount") or (gross - discount - adv_adj + vat - ait - retention + freight + other_tax))
        if net_payable < 0:
            net_payable = 0.0
        owing = float(data.get("outstanding_amount") or (net_payable - float(data.get("paid_amount") or 0.0)))
        entry_dt = data.get("entry_date") or data.get("bill_date") or str(datetime.date.today())
        cat = data.get("bill_category") or data.get("bill_type") or "STANDARD_PURCHASE"

        if existing:
            sql = """
                UPDATE ap_purchase_bills SET
                    bill_number = ?, entry_date = ?, bill_category = ?, purch_org_id = ?,
                    project_id = ?, deed_reference = ?, purchase_item_type = ?, procurement_type = ?,
                    is_ait_deductible = ?, is_checked_and_released = ?, vendor_id = ?,
                    pay_to_vendor_id = ?, vendor_invoice_no = ?, vendor_invoice_date = ?,
                    effective_invoice_date = ?, description = ?, gross_amount = ?,
                    discount_amount = ?, advance_adjusted_amount = ?, vat_amount = ?,
                    ait_amount = ?, security_deposit_amount = ?, freight_amount = ?,
                    other_tax_amount = ?, net_payable_amount = ?, owing_balance = ?,
                    credit_period_days = ?, due_date = ?, comments = ?, status = ?
                WHERE id = ?
            """
            db.execute(sql, (
                data.get("bill_number"), entry_dt, cat,
                data.get("purch_org_id"), data.get("project_id"), data.get("deed_reference"),
                data.get("purchase_item_type", "MATERIALS"), data.get("procurement_type", "LOCAL"),
                1 if data.get("is_ait_deductible", True) else 0, 1 if data.get("is_checked_and_released", False) else 0,
                data.get("vendor_id"), data.get("pay_to_vendor_id"), data.get("vendor_invoice_no") or data.get("vendor_challan_number"),
                data.get("vendor_invoice_date"), data.get("effective_invoice_date"), data.get("description"),
                gross, discount, adv_adj, vat, ait, retention, freight, other_tax,
                net_payable, owing, int(data.get("credit_period_days") or 30), data.get("due_date"),
                data.get("comments"), data.get("status", "APPROVED"), bill_id
            ))
        else:
            sql = """
                INSERT INTO ap_purchase_bills (
                    id, company_id, bill_number, entry_date, bill_category, purch_org_id,
                    project_id, deed_reference, purchase_item_type, procurement_type,
                    is_ait_deductible, is_checked_and_released, vendor_id, pay_to_vendor_id,
                    vendor_invoice_no, vendor_invoice_date, effective_invoice_date, description,
                    gross_amount, discount_amount, advance_adjusted_amount, vat_amount,
                    ait_amount, security_deposit_amount, freight_amount, other_tax_amount,
                    net_payable_amount, paid_amount, owing_balance, credit_period_days,
                    due_date, comments, status, created_by
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?
                )
            """
            db.execute(sql, (
                bill_id, data.get("company_id"), data.get("bill_number"), entry_dt,
                cat, data.get("purch_org_id"),
                data.get("project_id"), data.get("deed_reference"), data.get("purchase_item_type", "MATERIALS"),
                data.get("procurement_type", "LOCAL"), 1 if data.get("is_ait_deductible", True) else 0,
                1 if data.get("is_checked_and_released", False) else 0, data.get("vendor_id"),
                data.get("pay_to_vendor_id"), data.get("vendor_invoice_no") or data.get("vendor_challan_number"),
                data.get("vendor_invoice_date"), data.get("effective_invoice_date"), data.get("description"),
                gross, discount, adv_adj, vat, ait, retention, freight, other_tax,
                net_payable, owing, int(data.get("credit_period_days") or 30), data.get("due_date"),
                data.get("comments"), data.get("status", "APPROVED"), data.get("created_by", "System User")
            ))

        if grn_lines:
            db.execute("DELETE FROM ap_purchase_bill_grn_lines WHERE bill_id = ?", (bill_id,))
            for line in grn_lines:
                db.execute("""
                    INSERT INTO ap_purchase_bill_grn_lines (
                        id, bill_id, grn_number, grn_date, po_number, warehouse_name, item_description, cost_amount, freight_amount, net_matched_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), bill_id, line.get("grn_number"), line.get("grn_date"),
                    line.get("po_number"), line.get("warehouse_name"), line.get("item_description"),
                    float(line.get("cost_amount") or 0.0), float(line.get("freight_amount") or 0.0),
                    float(line.get("net_matched_amount") or 0.0)
                ))

        return bill_id

    @staticmethod
    def save_landowner_bill(data: Dict[str, Any]) -> str:
        bill_data = {
            "company_id": data.get("company_id"),
            "bill_number": f"DEED-BILL-{datetime.date.today().strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}",
            "entry_date": data.get("installment_due_date") or str(datetime.date.today()),
            "bill_category": "LANDOWNER_CONTRACT",
            "vendor_id": data.get("vendor_id"),
            "deed_reference": data.get("agreement_deed_no"),
            "description": f"{data.get('project_name')} - {data.get('installment_title')}: {data.get('description', '')}",
            "gross_amount": float(data.get("gross_milestone_amount") or 0.0),
            "ait_amount": float(data.get("tax_amount") or 0.0),
            "other_tax_amount": float(data.get("holding_tax_amount") or 0.0),
            "net_payable_amount": float(data.get("net_payable_amount") or 0.0),
            "due_date": data.get("installment_due_date") or str(datetime.date.today()),
            "status": "APPROVED"
        }
        return APTransactionService.save_purchase_bill(bill_data)

    @staticmethod
    def get_available_grns_for_vendor(vendor_id: str, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT TOP 10 * FROM inv_grn_headers WHERE 1=1"
        params = []
        if company_id:
            sql += " AND company_id = ?"
            params.append(company_id)
        sql += " ORDER BY grn_date DESC"
        return db.query(sql, tuple(params))


class APKnockOffService:
    @staticmethod
    def get_advance_adjustments(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT a.*,
                   a.adjustment_number AS voucher_number,
                   a.adjusted_amount AS adjustment_amount,
                   a.narration AS remarks,
                   v.vendor_code, v.vendor_name,
                   b.bill_number, b.vendor_invoice_no,
                   p.payment_number AS advance_payment_number
            FROM ap_advance_adjustments a
            JOIN sourcing_vendors v ON a.vendor_id = v.id
            LEFT JOIN ap_purchase_bills b ON a.bill_id = b.id
            LEFT JOIN ap_vendor_payments p ON a.payment_voucher_id = p.id
            WHERE a.company_id = ? AND COALESCE(a.isDelete, 0) = 0
            ORDER BY a.code DESC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_unsettled_advances_for_vendor(vendor_id: str, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.id, p.payment_number, p.payment_date,
                   COALESCE(p.net_disbursed_amount, p.gross_bills_amount) AS gross_payment_amount,
                   COALESCE(p.net_disbursed_amount, p.gross_bills_amount) AS unadjusted_amount,
                   p.currency, v.vendor_code, v.vendor_name
            FROM ap_vendor_payments p
            JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE p.vendor_id = ? AND p.status IN ('POSTED', 'CLEARED')
        """
        params = [vendor_id]
        if company_id:
            sql += " AND p.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY p.payment_date DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_unsettled_advances(company_id: str, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if vendor_id:
            return APKnockOffService.get_unsettled_advances_for_vendor(vendor_id, company_id)
        sql = """
            SELECT p.id, p.payment_number, p.payment_date,
                   COALESCE(p.net_disbursed_amount, p.gross_bills_amount) AS gross_payment_amount,
                   COALESCE(p.net_disbursed_amount, p.gross_bills_amount) AS unadjusted_amount,
                   p.currency, v.vendor_code, v.vendor_name
            FROM ap_vendor_payments p
            JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE p.company_id = ? AND p.status IN ('POSTED', 'CLEARED')
            ORDER BY p.payment_date DESC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_open_bills_for_vendor(vendor_id: str, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT b.id, b.bill_number, b.vendor_invoice_no,
                   COALESCE(b.entry_date, b.effective_invoice_date) AS bill_date,
                   b.due_date, b.net_payable_amount, b.paid_amount,
                   COALESCE(b.owing_balance, b.net_payable_amount) AS outstanding_amount,
                   v.vendor_code, v.vendor_name
            FROM ap_purchase_bills b
            JOIN sourcing_vendors v ON b.vendor_id = v.id
            WHERE b.vendor_id = ? AND COALESCE(b.owing_balance, b.net_payable_amount) > 0 AND COALESCE(b.isDelete, 0) = 0
        """
        params = [vendor_id]
        if company_id:
            sql += " AND b.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY b.due_date ASC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_open_purchase_bills(company_id: str, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if vendor_id:
            return APKnockOffService.get_open_bills_for_vendor(vendor_id, company_id)
        sql = """
            SELECT b.id, b.bill_number, b.vendor_invoice_no,
                   COALESCE(b.entry_date, b.effective_invoice_date) AS bill_date,
                   b.due_date, b.net_payable_amount, b.paid_amount,
                   COALESCE(b.owing_balance, b.net_payable_amount) AS outstanding_amount,
                   v.vendor_code, v.vendor_name
            FROM ap_purchase_bills b
            JOIN sourcing_vendors v ON b.vendor_id = v.id
            WHERE b.company_id = ? AND COALESCE(b.owing_balance, b.net_payable_amount) > 0 AND COALESCE(b.isDelete, 0) = 0
            ORDER BY b.due_date ASC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def save_advance_adjustment(data: Dict[str, Any]) -> str:
        adj_id = data.get("id") or str(uuid.uuid4())
        adj_num = data.get("voucher_number") or f"ADJ-{datetime.date.today().strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}"
        adj_amt = float(data.get("adjustment_amount") or 0.0)
        bill_id = data.get("purchase_bill_id") or data.get("bill_id")

        db.execute("""
            INSERT INTO ap_advance_adjustments (
                id, company_id, adjustment_number, adjustment_date, vendor_id,
                payment_voucher_id, bill_id, adjusted_amount, narration, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'POSTED', ?)
        """, (
            adj_id, data.get("company_id"), adj_num,
            data.get("adjustment_date", str(datetime.date.today())),
            data.get("vendor_id"), data.get("payment_voucher_id"), bill_id,
            adj_amt, data.get("remarks") or data.get("narration", "Prepayment knock-off"),
            data.get("created_by", "Finance User")
        ))

        if bill_id:
            db.execute("""
                UPDATE ap_purchase_bills SET
                    advance_adjusted_amount = COALESCE(advance_adjusted_amount, 0) + ?,
                    owing_balance = CASE WHEN owing_balance - ? < 0 THEN 0 ELSE owing_balance - ? END
                WHERE id = ?
            """, (adj_amt, adj_amt, adj_amt, bill_id))

        return adj_id

    @staticmethod
    def post_advance_knock_off(company_id: str, vendor_id: str, adjustment_date: str, bill_id: str, voucher_id: Optional[str], adjusted_amount: float, narration: str, user_name: str = "Finance User") -> str:
        return APKnockOffService.save_advance_adjustment({
            "company_id": company_id,
            "vendor_id": vendor_id,
            "adjustment_date": adjustment_date,
            "purchase_bill_id": bill_id,
            "payment_voucher_id": voucher_id,
            "adjustment_amount": adjusted_amount,
            "remarks": narration,
            "created_by": user_name
        })


class APDisbursementService:
    @staticmethod
    def get_payment_orders(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT o.*,
                   COALESCE(o.total_order_amount, 0.0) AS total_proposed_amount,
                   v.vendor_code, v.vendor_name
            FROM ap_payment_orders o
            LEFT JOIN ap_payment_order_lines l ON o.id = l.order_id
            LEFT JOIN sourcing_vendors v ON l.vendor_id = v.id
            WHERE o.company_id = ? AND COALESCE(o.isDelete, 0) = 0
            ORDER BY o.code DESC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_payment_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT o.*,
                   COALESCE(o.total_order_amount, 0.0) AS total_proposed_amount,
                   v.id AS vendor_id, v.vendor_code, v.vendor_name
            FROM ap_payment_orders o
            LEFT JOIN ap_payment_order_lines l ON o.id = l.order_id
            LEFT JOIN sourcing_vendors v ON l.vendor_id = v.id
            WHERE o.id = ?
        """
        return db.query_one(sql, (order_id,))

    @staticmethod
    def get_payment_order_lines(order_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT l.*, b.bill_number, b.vendor_invoice_no, b.entry_date, b.due_date,
                   b.net_payable_amount, v.vendor_code, v.vendor_name
            FROM ap_payment_order_lines l
            LEFT JOIN ap_purchase_bills b ON l.bill_id = b.id
            JOIN sourcing_vendors v ON l.vendor_id = v.id
            WHERE l.order_id = ?
            ORDER BY l.line_no ASC
        """
        return db.query(sql, (order_id,))

    @staticmethod
    def save_payment_order(data: Dict[str, Any], lines: Optional[List[Dict[str, Any]]] = None) -> str:
        order_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM ap_payment_orders WHERE id = ?", (order_id,))
        total_amt = float(data.get("total_proposed_amount") or data.get("total_order_amount") or 0.0)

        if existing:
            db.execute("""
                UPDATE ap_payment_orders SET
                    order_number = ?, order_date = ?, total_order_amount = ?,
                    purpose_notes = ?, status = ?
                WHERE id = ?
            """, (
                data.get("order_number"), data.get("order_date"),
                total_amt, data.get("remarks") or data.get("purpose_notes"),
                data.get("status", "APPROVED"), order_id
            ))
        else:
            db.execute("""
                INSERT INTO ap_payment_orders (
                    id, company_id, order_number, order_date, pay_from_type, bank_account_id,
                    currency, exchange_rate, fiscal_year, fiscal_period, total_order_amount,
                    purpose_notes, status, created_by
                ) VALUES (?, ?, ?, ?, 'BANK', ?, 'BDT', 1.0, '2026-2027', 1, ?, ?, ?, ?)
            """, (
                order_id, data.get("company_id"), data.get("order_number"), data.get("order_date"),
                data.get("bank_account_id"), total_amt,
                data.get("remarks") or data.get("purpose_notes"), data.get("status", "APPROVED"),
                data.get("created_by", "Treasury Lead")
            ))

        vendor_id = data.get("vendor_id")
        if vendor_id and not lines:
            lines = [{"vendor_id": vendor_id, "allocated_amount": total_amt}]

        if lines:
            db.execute("DELETE FROM ap_payment_order_lines WHERE order_id = ?", (order_id,))
            for idx, line in enumerate(lines, 1):
                db.execute("""
                    INSERT INTO ap_payment_order_lines (id, order_id, line_no, payment_against, bill_id, vendor_id, allocated_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), order_id, idx, line.get("payment_against", "PURCHASE_BILL"),
                    line.get("bill_id"), line.get("vendor_id") or vendor_id, float(line.get("allocated_amount") or total_amt)
                ))

        return order_id

    @staticmethod
    def get_vendor_payments(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.*,
                   COALESCE(p.gross_bills_amount, 0.0) AS gross_payment_amount,
                   COALESCE(p.total_ait_withheld, 0.0) AS withheld_ait_amount,
                   COALESCE(p.net_disbursed_amount, 0.0) AS net_disbursement_amount,
                   o.order_number,
                   v.vendor_code, v.vendor_name
            FROM ap_vendor_payments p
            LEFT JOIN ap_payment_orders o ON p.payment_order_id = o.id
            LEFT JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE p.company_id = ? AND COALESCE(p.isDelete, 0) = 0
            ORDER BY p.code DESC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_vendor_payment_by_id(payment_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT p.*,
                   COALESCE(p.gross_bills_amount, 0.0) AS gross_payment_amount,
                   COALESCE(p.total_ait_withheld, 0.0) AS withheld_ait_amount,
                   COALESCE(p.net_disbursed_amount, 0.0) AS net_disbursement_amount,
                   o.order_number,
                   v.vendor_code, v.vendor_name
            FROM ap_vendor_payments p
            LEFT JOIN ap_payment_orders o ON p.payment_order_id = o.id
            LEFT JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE p.id = ?
        """
        return db.query_one(sql, (payment_id,))

    @staticmethod
    def get_vendor_payment_lines(payment_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT l.*, b.bill_number, b.vendor_invoice_no, b.entry_date, b.due_date,
                   v.vendor_code, v.vendor_name
            FROM ap_vendor_payment_lines l
            LEFT JOIN ap_purchase_bills b ON l.bill_id = b.id
            JOIN sourcing_vendors v ON l.vendor_id = v.id
            WHERE l.payment_id = ?
            ORDER BY l.line_no ASC
        """
        return db.query(sql, (payment_id,))

    @staticmethod
    def save_vendor_payment(data: Dict[str, Any], lines: Optional[List[Dict[str, Any]]] = None) -> str:
        payment_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM ap_vendor_payments WHERE id = ?", (payment_id,))

        gross = float(data.get("gross_payment_amount") or data.get("gross_bills_amount") or 0.0)
        discount = float(data.get("discount_amount") or 0.0)
        ait = float(data.get("withheld_ait_amount") or data.get("total_ait_withheld") or 0.0)
        net_paid = float(data.get("net_disbursement_amount") or data.get("net_disbursed_amount") or (gross - discount - ait))

        if existing:
            db.execute("""
                UPDATE ap_vendor_payments SET
                    payment_number = ?, payment_date = ?, vendor_id = ?, payment_order_id = ?, pay_from_type = ?,
                    bank_account_id = ?, payment_method = ?, transaction_ref = ?, gross_bills_amount = ?,
                    discount_amount = ?, total_ait_withheld = ?, net_disbursed_amount = ?,
                    narration = ?, status = ?
                WHERE id = ?
            """, (
                data.get("payment_number"), data.get("payment_date"), data.get("vendor_id"),
                data.get("payment_order_id"), data.get("pay_from_type", "BANK"), data.get("bank_account_id"),
                data.get("payment_method", "BANK_TRANSFER"), data.get("cheque_number") or data.get("transaction_ref"),
                gross, discount, ait, net_paid,
                data.get("description") or data.get("narration"), data.get("status", "CLEARED"), payment_id
            ))
        else:
            db.execute("""
                INSERT INTO ap_vendor_payments (
                    id, company_id, payment_number, payment_date, vendor_id, payment_order_id, pay_from_type,
                    bank_account_id, payment_method, transaction_ref, currency, exchange_rate,
                    fiscal_year, fiscal_period, gross_bills_amount, discount_amount,
                    total_ait_withheld, net_disbursed_amount, narration, status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'BDT', 1.0, '2026-2027', 1, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payment_id, data.get("company_id"), data.get("payment_number"), data.get("payment_date"),
                data.get("vendor_id"), data.get("payment_order_id"), data.get("pay_from_type", "BANK"),
                data.get("bank_account_id"), data.get("payment_method", "BANK_TRANSFER"),
                data.get("cheque_number") or data.get("transaction_ref"),
                gross, discount, ait, net_paid,
                data.get("description") or data.get("narration"), data.get("status", "CLEARED"),
                data.get("created_by", "Disbursement Officer")
            ))

        return payment_id


class APTaxRemittanceService:
    @staticmethod
    def get_pending_withheld_ait_lines(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.id AS payment_id, p.payment_number, p.payment_date,
                   COALESCE(p.total_ait_withheld, 0.0) AS ait_amount,
                   COALESCE(p.gross_bills_amount, 0.0) AS gross_amount,
                   v.vendor_code, v.vendor_name, v.tax_id_tin AS tin_number
            FROM ap_vendor_payments p
            JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE p.company_id = ? AND COALESCE(p.total_ait_withheld, 0) > 0
            ORDER BY p.payment_date DESC
        """
        return db.query(sql, (company_id,))

    @staticmethod
    def get_unremitted_ait_deductions(company_id: str) -> List[Dict[str, Any]]:
        return APTaxRemittanceService.get_pending_withheld_ait_lines(company_id)

    @staticmethod
    def get_ait_remittances(company_id: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM ap_ait_remittances WHERE company_id = ? AND COALESCE(isDelete, 0) = 0 ORDER BY code DESC"
        return db.query(sql, (company_id,))

    @staticmethod
    def save_ait_remittance(data: Dict[str, Any]) -> str:
        remit_id = data.get("id") or str(uuid.uuid4())
        remit_num = data.get("remittance_number") or f"AIT-REM-{datetime.date.today().strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}"
        challan_no = data.get("challan_number") or data.get("treasury_challan_no")
        total_amt = float(data.get("total_remitted_amount") or 0.0)

        db.execute("""
            INSERT INTO ap_ait_remittances (
                id, company_id, remittance_number, remittance_date, treasury_challan_no,
                challan_date, tax_authority_name, tax_section, tax_zone, tax_circle,
                bank_name, bank_branch, total_remitted_amount, fiscal_year, remarks, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'SECTION_52', ?, ?, ?, ?, ?, ?, ?, 'POSTED', ?)
        """, (
            remit_id, data.get("company_id"), remit_num,
            data.get("remittance_date", str(datetime.date.today())),
            challan_no, data.get("challan_date", str(datetime.date.today())),
            data.get("tax_authority_name", "National Board of Revenue (NBR)"),
            data.get("tax_zone", "Zone 01"), data.get("tax_circle", "Circle 02"),
            data.get("bank_name", "Bangladesh Bank"), data.get("bank_branch", "Motijheel Principal Branch"),
            total_amt, data.get("assessment_year", "2026-2027"),
            data.get("remarks", ""), data.get("created_by", "Tax Officer")
        ))
        return remit_id

    @staticmethod
    def post_ait_remittance(company_id: str, treasury_challan_no: str, remittance_date: str, deduction_ids: List[str], total_amount: float, bank_account_id: Optional[str] = None, remarks: str = "", user_name: str = "Tax Officer") -> str:
        return APTaxRemittanceService.save_ait_remittance({
            "company_id": company_id,
            "treasury_challan_no": treasury_challan_no,
            "remittance_date": remittance_date,
            "total_remitted_amount": total_amount,
            "bank_account_id": bank_account_id,
            "remarks": remarks,
            "created_by": user_name
        })


class APNoteService:
    @staticmethod
    def get_ap_notes(company_id: str, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT n.*,
                   COALESCE(n.amount, 0.0) AS gross_amount,
                   COALESCE(n.amount, 0.0) * 0.85 AS subtotal_amount,
                   COALESCE(n.amount, 0.0) * 0.15 AS vat_amount,
                   n.description AS reason_description,
                   v.vendor_code, v.vendor_name, b.bill_number, b.vendor_invoice_no
            FROM ap_notes n
            JOIN sourcing_vendors v ON n.vendor_id = v.id
            LEFT JOIN ap_purchase_bills b ON n.bill_id = b.id
            WHERE n.company_id = ? AND COALESCE(n.isDelete, 0) = 0
        """
        params = [company_id]
        if note_type:
            sql += " AND n.note_type = ?"
            params.append(note_type)
        sql += " ORDER BY n.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_notes(company_id: str, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return APNoteService.get_ap_notes(company_id, note_type)

    @staticmethod
    def get_ap_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT n.*,
                   COALESCE(n.amount, 0.0) AS gross_amount,
                   COALESCE(n.amount, 0.0) * 0.85 AS subtotal_amount,
                   COALESCE(n.amount, 0.0) * 0.15 AS vat_amount,
                   n.description AS reason_description,
                   v.vendor_code, v.vendor_name, v.office_address AS vendor_address,
                   b.bill_number, b.vendor_invoice_no
            FROM ap_notes n
            JOIN sourcing_vendors v ON n.vendor_id = v.id
            LEFT JOIN ap_purchase_bills b ON n.bill_id = b.id
            WHERE n.id = ?
        """
        return db.query_one(sql, (note_id,))

    @staticmethod
    def get_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
        return APNoteService.get_ap_note_by_id(note_id)

    @staticmethod
    def save_ap_note(data: Dict[str, Any]) -> str:
        note_id = data.get("id") or str(uuid.uuid4())
        existing = db.query_one("SELECT id FROM ap_notes WHERE id = ?", (note_id,))
        amount = float(data.get("gross_amount") or data.get("amount") or 0.0)

        if existing:
            db.execute("""
                UPDATE ap_notes SET
                    note_type = ?, note_number = ?, note_date = ?, flow_type = ?,
                    bill_id = ?, vendor_id = ?, reason_code = ?, amount = ?,
                    description = ?, status = ?
                WHERE id = ?
            """, (
                data.get("note_type", "DEBIT"), data.get("note_number"), data.get("note_date"),
                data.get("flow_type", "REF"), data.get("purchase_bill_id") or data.get("bill_id"),
                data.get("vendor_id"), data.get("reason_code"), amount,
                data.get("reason_description") or data.get("description"), data.get("status", "APPROVED"),
                note_id
            ))
        else:
            db.execute("""
                INSERT INTO ap_notes (
                    id, company_id, note_type, note_number, note_date, flow_type,
                    bill_id, vendor_id, reason_code, amount, description, status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                note_id, data.get("company_id"), data.get("note_type", "DEBIT"), data.get("note_number"),
                data.get("note_date"), data.get("flow_type", "REF"),
                data.get("purchase_bill_id") or data.get("bill_id"), data.get("vendor_id"),
                data.get("reason_code"), amount, data.get("reason_description") or data.get("description"),
                data.get("status", "APPROVED"), data.get("created_by", "Accounting User")
            ))

        return note_id

    @staticmethod
    def save_note(data: Dict[str, Any]) -> str:
        return APNoteService.save_ap_note(data)


class APReversalService:
    @staticmethod
    def reverse_purchase_bill(bill_id: str, reason: str = "Audited reversal", user_id: Optional[str] = None) -> bool:
        db.execute("""
            UPDATE ap_purchase_bills SET
                is_reversed = 1, reversal_date = ?, reversal_reason = ?,
                status = 'REVERSED', owing_balance = 0
            WHERE id = ?
        """, (str(datetime.date.today()), reason, bill_id))
        return True

    @staticmethod
    def reverse_vendor_payment(payment_id: str, reason: str = "Audited reversal", user_id: Optional[str] = None) -> bool:
        db.execute("""
            UPDATE ap_vendor_payments SET
                status = 'REVERSED', narration = narration + ' [REVERSED: ' + ? + ']'
            WHERE id = ?
        """, (reason, payment_id))
        return True

    @staticmethod
    def execute_bill_reversal(bill_id: str, reason: str, reversal_date: str, user_name: str = "Auditor") -> bool:
        return APReversalService.reverse_purchase_bill(bill_id, reason)

    @staticmethod
    def get_posted_bills_for_reversal(company_id: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT b.id, b.bill_number, b.entry_date, b.vendor_invoice_no, b.gross_amount,
                   b.net_payable_amount, b.status, b.is_reversed,
                   v.vendor_code, v.vendor_name
            FROM ap_purchase_bills b
            JOIN sourcing_vendors v ON b.vendor_id = v.id
            WHERE b.company_id = ? AND COALESCE(b.is_reversed, 0) = 0 AND COALESCE(b.isDelete, 0) = 0
            ORDER BY b.entry_date DESC
        """
        return db.query(sql, (company_id,))


class APDocumentService:
    @staticmethod
    def get_grn_documents(company_id: Optional[str] = None, grn_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT d.*,
                   COALESCE(d.document_category, 'INSPECTION_CERTIFICATE') AS document_type,
                   COALESCE(d.is_verified, 1) AS is_verified_val,
                   CASE WHEN d.is_verified = 1 THEN 'VERIFIED' ELSE 'PENDING_QC' END AS verification_status,
                   COALESCE(g.supplier_name, 'Apex Steel Works') AS vendor_name,
                   COALESCE(g.grn_number, 'GRN-2026-0112') AS grn_number
            FROM ap_grn_documents d
            LEFT JOIN inv_grn_headers g ON d.grn_id = g.id
            WHERE 1=1
        """
        params = []
        if grn_id:
            sql += " AND d.grn_id = ?"
            params.append(grn_id)
        sql += " ORDER BY d.uploaded_at DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def save_grn_document(data: Dict[str, Any]) -> str:
        doc_id = str(uuid.uuid4())
        db.execute("""
            INSERT INTO ap_grn_documents (
                id, grn_id, grn_number, document_category, file_name, file_path, file_size_bytes, mime_type,
                uploaded_by, is_verified, verified_by
            ) VALUES (?, ?, ?, ?, ?, ?, 102400, 'application/pdf', 'QC Lead', 1, 'Chief Inspector')
        """, (
            doc_id, data.get("grn_id"), data.get("grn_number", "GRN-2026-0082"),
            data.get("document_type", "INSPECTION_CERTIFICATE"),
            data.get("file_name", "GRN_Inspection_Report.pdf"),
            data.get("file_path", "/vault/ap_grn/inspection.pdf")
        ))
        return doc_id

    @staticmethod
    def get_payment_documents(company_id: Optional[str] = None, payment_id: Optional[str] = None, payment_order_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT d.*,
                   COALESCE(d.document_category, 'BANK_ADVICE') AS document_type,
                   p.payment_number, p.payment_date,
                   COALESCE(p.net_disbursed_amount, 0.0) AS net_disbursement_amount,
                   v.vendor_code, v.vendor_name
            FROM ap_payment_documents d
            LEFT JOIN ap_vendor_payments p ON d.payment_id = p.id
            LEFT JOIN sourcing_vendors v ON p.vendor_id = v.id
            WHERE 1=1
        """
        params = []
        if payment_id:
            sql += " AND d.payment_id = ?"
            params.append(payment_id)
        if payment_order_id:
            sql += " AND d.payment_order_id = ?"
            params.append(payment_order_id)
        sql += " ORDER BY d.uploaded_at DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def save_payment_document(data: Dict[str, Any]) -> str:
        doc_id = str(uuid.uuid4())
        db.execute("""
            INSERT INTO ap_payment_documents (
                id, payment_id, payment_order_id, document_category, file_name, file_path, file_size_bytes, mime_type,
                uploaded_by, is_verified, verified_by
            ) VALUES (?, ?, NULL, ?, ?, ?, 204800, 'application/pdf', 'Treasury Officer', 1, 'Treasury Manager')
        """, (
            doc_id, data.get("payment_id"),
            data.get("document_type", "BANK_ADVICE"),
            data.get("file_name", "Treasury_Remittance_Slip.pdf"),
            data.get("file_path", "/vault/ap_proofs/remittance.pdf")
        ))
        return doc_id


class APReportService:
    @staticmethod
    def get_ap_schedule_report(company_id: str, as_of_date: Optional[str] = None) -> Dict[str, Any]:
        bills = db.query("""
            SELECT v.id AS vendor_id, v.vendor_code, v.vendor_name,
                   0.0 AS opening_balance,
                   COALESCE(SUM(b.net_payable_amount), 0.0) AS invoiced_amount,
                   COALESCE(SUM(b.paid_amount), 0.0) AS paid_amount,
                   COALESCE(SUM(b.advance_adjusted_amount), 0.0) AS adjusted_amount,
                   COALESCE(SUM(b.owing_balance), 0.0) AS closing_balance
            FROM sourcing_vendors v
            LEFT JOIN ap_purchase_bills b ON v.id = b.vendor_id AND b.company_id = ? AND COALESCE(b.isDelete, 0) = 0
            GROUP BY v.id, v.vendor_code, v.vendor_name
            HAVING COALESCE(SUM(b.net_payable_amount), 0) > 0
            ORDER BY closing_balance DESC
        """, (company_id,))

        totals = {
            "total_invoiced": sum(float(r["invoiced_amount"]) for r in bills),
            "total_paid": sum(float(r["paid_amount"]) for r in bills),
            "total_adjusted": sum(float(r["adjusted_amount"]) for r in bills),
            "total_closing": sum(float(r["closing_balance"]) for r in bills)
        }
        return {"rows": bills, "totals": totals}

    @staticmethod
    def get_ap_schedule(company_id: str) -> Dict[str, Any]:
        return APReportService.get_ap_schedule_report(company_id)

    @staticmethod
    def get_vendor_statement(vendor_id: str, company_id: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, Any]:
        vendor = db.query_one("SELECT * FROM sourcing_vendors WHERE id = ?", (vendor_id,))
        lines = []
        running_bal = 0.0

        # Fetch bills
        sql_bills = "SELECT id, bill_number AS doc_number, entry_date AS date, description, net_payable_amount AS credit FROM ap_purchase_bills WHERE vendor_id = ? AND COALESCE(isDelete, 0) = 0"
        params_b = [vendor_id]
        if company_id:
            sql_bills += " AND company_id = ?"
            params_b.append(company_id)
        bills = db.query(sql_bills, tuple(params_b))
        for b in bills:
            lines.append({
                "date": str(b["date"] or "2026-09-01"),
                "doc_type": "BILL",
                "doc_number": b["doc_number"],
                "description": b["description"] or "Purchase Invoicing",
                "debit": 0.0,
                "credit": float(b["credit"] or 0.0)
            })

        # Fetch payments
        sql_pmt = "SELECT id, payment_number AS doc_number, payment_date AS date, narration AS description, net_disbursed_amount AS debit FROM ap_vendor_payments WHERE vendor_id = ? AND COALESCE(isDelete, 0) = 0"
        params_p = [vendor_id]
        if company_id:
            sql_pmt += " AND company_id = ?"
            params_p.append(company_id)
        pmts = db.query(sql_pmt, tuple(params_p))
        for p in pmts:
            lines.append({
                "date": str(p["date"] or "2026-09-05"),
                "doc_type": "PAYMENT",
                "doc_number": p["doc_number"],
                "description": p["description"] or "Treasury Bank Transfer",
                "debit": float(p["debit"] or 0.0),
                "credit": 0.0
            })

        lines.sort(key=lambda x: x["date"])
        for line in lines:
            running_bal += (line["credit"] - line["debit"])
            line["running_balance"] = running_bal

        return {
            "vendor": vendor,
            "lines": lines,
            "totals": {
                "total_debit": sum(l["debit"] for l in lines),
                "total_credit": sum(l["credit"] for l in lines),
                "closing_balance": running_bal
            }
        }

    @staticmethod
    def get_tax_1099_summary(company_id: str, fiscal_year: Optional[str] = None) -> Dict[str, Any]:
        records = db.query("""
            SELECT v.vendor_code, v.vendor_name, v.tax_id_tin AS tin_number,
                   COALESCE(SUM(b.gross_amount), 0.0) AS total_billed,
                   COALESCE(SUM(b.ait_amount), 0.0) AS total_ait,
                   COALESCE(SUM(b.vat_amount), 0.0) AS total_vat
            FROM sourcing_vendors v
            JOIN ap_purchase_bills b ON v.id = b.vendor_id AND b.company_id = ? AND COALESCE(b.isDelete, 0) = 0
            GROUP BY v.vendor_code, v.vendor_name, v.tax_id_tin
            HAVING COALESCE(SUM(b.gross_amount), 0.0) > 0
            ORDER BY total_billed DESC
        """, (company_id,))

        totals = {
            "total_billed": sum(float(r["total_billed"]) for r in records),
            "total_ait": sum(float(r["total_ait"]) for r in records),
            "total_vat": sum(float(r["total_vat"]) for r in records)
        }
        return {"records": records, "totals": totals}
