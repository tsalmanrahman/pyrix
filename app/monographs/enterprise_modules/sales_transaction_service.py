from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class SalesTransactionService:

    # =========================================================================
    # 1. SALES QUOTES (Quotes, Proformas, Revisions)
    # =========================================================================
    @staticmethod
    def get_quotes(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT q.*, sp.full_name AS salesperson_name, c.short_code AS company_code,
               (SELECT COUNT(*) FROM sales_quote_items qi WHERE qi.quote_id = q.id) AS item_count
        FROM sales_quotes q
        JOIN companies c ON q.company_id = c.id
        LEFT JOIN salespersons sp ON q.salesperson_id = sp.id
        """
        params = ()
        if company_id:
            sql += " WHERE q.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY q.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_quote_by_id(quote_id: str) -> Optional[Dict[str, Any]]:
        quote = db.query_one(
            """
            SELECT q.*, sp.full_name AS salesperson_name, c.name AS company_name, c.short_code AS company_code, c.currency AS company_currency
            FROM sales_quotes q
            JOIN companies c ON q.company_id = c.id
            LEFT JOIN salespersons sp ON q.salesperson_id = sp.id
            WHERE q.id = ?
            """,
            (quote_id,)
        )
        if not quote:
            return None
        quote["items"] = db.query("SELECT * FROM sales_quote_items WHERE quote_id = ? ORDER BY code ASC", (quote_id,))
        return quote

    @staticmethod
    def create_quote(
        company_id: str,
        quote_number: str,
        customer_name: str,
        salesperson_id: Optional[str],
        quote_date: str,
        valid_until: str,
        items: List[Dict[str, Any]],
        currency: str = "USD",
        discount_amount: float = 0.0,
        tax_amount: float = 0.0,
        progress_notes: Optional[str] = None
    ) -> str:
        new_id = str(uuid.uuid4())
        subtotal = sum(float(it.get("quantity", 0)) * float(it.get("unit_price", 0)) for it in items)
        total_amount = subtotal - discount_amount + tax_amount

        db.execute(
            """
            INSERT INTO sales_quotes 
            (id, company_id, quote_number, revision_no, customer_name, salesperson_id, quote_date, valid_until, subtotal, discount_amount, tax_amount, total_amount, currency, status, progress_notes)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', ?)
            """,
            (new_id, company_id, quote_number.strip(), customer_name.strip(), salesperson_id, quote_date, valid_until, subtotal, discount_amount, tax_amount, total_amount, currency, progress_notes)
        )

        for it in items:
            q_val = float(it.get("quantity", 1))
            p_val = float(it.get("unit_price", 0))
            disc = float(it.get("discount_pct", 0))
            l_tot = q_val * p_val * (1.0 - (disc / 100.0))
            db.execute(
                """
                INSERT INTO sales_quote_items (quote_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_id, it.get("item_code", "ITM"), it.get("item_name", "Item"), it.get("uom", "PCS"), q_val, p_val, disc, l_tot, it.get("remarks", ""))
            )
        return new_id

    # =========================================================================
    # 2. SALES ORDERS (SO Management)
    # =========================================================================
    @staticmethod
    def get_orders(company_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT o.*, sp.full_name AS salesperson_name, c.short_code AS company_code,
               (SELECT COUNT(*) FROM sales_order_items oi WHERE oi.order_id = o.id) AS item_count,
               (SELECT COUNT(*) FROM sales_delivery_orders do WHERE do.order_id = o.id) AS do_count,
               (SELECT COUNT(*) FROM sales_invoices inv WHERE inv.order_id = o.id) AS inv_count
        FROM sales_orders o
        JOIN companies c ON o.company_id = c.id
        LEFT JOIN salespersons sp ON o.salesperson_id = sp.id
        WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND o.company_id = ?"
            params.append(company_id)
        if status:
            sql += " AND o.status = ?"
            params.append(status)
        sql += " ORDER BY o.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
        order = db.query_one(
            """
            SELECT o.*, sp.full_name AS salesperson_name, c.name AS company_name, c.short_code AS company_code, c.currency AS company_currency
            FROM sales_orders o
            JOIN companies c ON o.company_id = c.id
            LEFT JOIN salespersons sp ON o.salesperson_id = sp.id
            WHERE o.id = ?
            """,
            (order_id,)
        )
        if not order:
            return None
        order["items"] = db.query("SELECT * FROM sales_order_items WHERE order_id = ? ORDER BY code ASC", (order_id,))
        order["delivery_orders"] = db.query("SELECT * FROM sales_delivery_orders WHERE order_id = ? ORDER BY code DESC", (order_id,))
        order["invoices"] = db.query("SELECT * FROM sales_invoices WHERE order_id = ? ORDER BY code DESC", (order_id,))
        order["approvals"] = db.query("SELECT * FROM sales_approvals WHERE entity_type = 'SO' AND entity_id = ? ORDER BY tier_level ASC", (order_id,))
        return order

    @staticmethod
    def create_sales_order(
        company_id: str,
        order_number: str,
        customer_name: str,
        salesperson_id: Optional[str],
        order_date: str,
        expected_delivery_date: str,
        payment_terms: str,
        delivery_terms: str,
        shipping_address: str,
        items: List[Dict[str, Any]],
        quote_id: Optional[str] = None,
        currency: str = "USD",
        discount_amount: float = 0.0,
        tax_amount: float = 0.0
    ) -> str:
        new_id = str(uuid.uuid4())
        subtotal = sum(float(it.get("quantity", 0)) * float(it.get("unit_price", 0)) for it in items)
        total_amount = subtotal - discount_amount + tax_amount

        db.execute(
            """
            INSERT INTO sales_orders 
            (id, company_id, quote_id, order_number, customer_name, salesperson_id, order_date, expected_delivery_date, payment_terms, delivery_terms, shipping_address, currency, subtotal, discount_amount, tax_amount, total_amount, status, is_on_hold, current_approval_tier, max_approval_tier, is_gl_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'APPROVED', 0, 1, 2, 0)
            """,
            (new_id, company_id, quote_id, order_number.strip(), customer_name.strip(), salesperson_id, order_date, expected_delivery_date, payment_terms, delivery_terms, shipping_address, currency, subtotal, discount_amount, tax_amount, total_amount)
        )

        for it in items:
            q_val = float(it.get("quantity", 1))
            p_val = float(it.get("unit_price", 0))
            disc = float(it.get("discount_pct", 0))
            l_tot = q_val * p_val * (1.0 - (disc / 100.0))
            db.execute(
                """
                INSERT INTO sales_order_items (order_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, packing_spec, delivered_qty, invoiced_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0)
                """,
                (new_id, it.get("item_code", "ITM"), it.get("item_name", "Item"), it.get("uom", "PCS"), q_val, p_val, disc, l_tot, it.get("packing_spec", "Standard Corrugated Pack"))
            )

        # If converted from quote, mark quote
        if quote_id:
            db.execute("UPDATE sales_quotes SET status = 'CONVERTED_TO_SO' WHERE id = ?", (quote_id,))

        return new_id

    # =========================================================================
    # 3. DELIVERY ORDERS (DO)
    # =========================================================================
    @staticmethod
    def get_delivery_orders(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT do.*, so.order_number, so.customer_name, c.short_code AS company_code,
               (SELECT COUNT(*) FROM sales_do_items doi WHERE doi.do_id = do.id) AS item_count
        FROM sales_delivery_orders do
        JOIN companies c ON do.company_id = c.id
        JOIN sales_orders so ON do.order_id = so.id
        """
        params = ()
        if company_id:
            sql += " WHERE do.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY do.code DESC"
        return db.query(sql, params)

    @staticmethod
    def create_delivery_order(
        company_id: str,
        order_id: str,
        do_number: str,
        do_date: str,
        dispatch_date: str,
        carrier_name: str,
        vehicle_no: str,
        tracking_ref: str,
        delivery_address: str,
        gate_pass_ref: Optional[str] = None,
        created_by: str = "Dispatch Officer"
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sales_delivery_orders 
            (id, company_id, order_id, do_number, do_date, dispatch_date, carrier_name, vehicle_no, tracking_ref, delivery_address, status, gate_pass_ref, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DISPATCHED', ?, ?)
            """,
            (new_id, company_id, order_id, do_number.strip(), do_date, dispatch_date, carrier_name, vehicle_no, tracking_ref, delivery_address, gate_pass_ref, created_by)
        )

        # Populate DO items from order items
        order_items = db.query("SELECT * FROM sales_order_items WHERE order_id = ?", (order_id,))
        for oi in order_items:
            db.execute(
                """
                INSERT INTO sales_do_items (do_id, order_item_id, item_code, item_name, uom, ordered_qty, dispatch_qty, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_id, oi["id"], oi["item_code"], oi["item_name"], oi["uom"], oi["quantity"], oi["quantity"], oi["unit_price"], oi["line_total"])
            )
            # Update delivered_qty on SO line
            db.execute("UPDATE sales_order_items SET delivered_qty = quantity WHERE id = ?", (oi["id"],))

        # Update SO status
        db.execute("UPDATE sales_orders SET status = 'DO_ISSUED' WHERE id = ?", (order_id,))
        return new_id

    # =========================================================================
    # 4. SALES INVOICES & REVERSALS
    # =========================================================================
    @staticmethod
    def get_invoices(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT inv.*, c.short_code AS company_code, so.order_number
        FROM sales_invoices inv
        JOIN companies c ON inv.company_id = c.id
        LEFT JOIN sales_orders so ON inv.order_id = so.id
        """
        params = ()
        if company_id:
            sql += " WHERE inv.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY inv.code DESC"
        return db.query(sql, params)

    @staticmethod
    def create_invoice_from_order(company_id: str, order_id: str, invoice_number: str, invoice_date: str, due_date: str) -> str:
        order = SalesTransactionService.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        do_row = db.query_one("SELECT TOP 1 id FROM sales_delivery_orders WHERE order_id = ? ORDER BY code DESC", (order_id,))
        new_id = str(uuid.uuid4())

        db.execute(
            """
            INSERT INTO sales_invoices 
            (id, company_id, order_id, do_id, invoice_number, invoice_type, customer_name, invoice_date, due_date, currency, exchange_rate, subtotal, discount_amount, tax_amount, total_amount, paid_amount, status, is_gl_posted, gl_journal_ref)
            VALUES (?, ?, ?, ?, ?, 'COMMERCIAL', ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 'ISSUED', 1, ?)
            """,
            (new_id, company_id, order_id, do_row["id"] if do_row else None, invoice_number.strip(), order["customer_name"], invoice_date, due_date, order["currency"], order.get("exchange_rate", 1.0), order["subtotal"], order["discount_amount"], order["tax_amount"], order["total_amount"], f"JV-SLS-{invoice_number}")
        )

        for oi in order["items"]:
            db.execute(
                """
                INSERT INTO sales_invoice_items (invoice_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_id, oi["item_code"], oi["item_name"], oi["uom"], oi["quantity"], oi["unit_price"], oi["discount_pct"], oi["line_total"])
            )
            db.execute("UPDATE sales_order_items SET invoiced_qty = quantity WHERE id = ?", (oi["id"],))

        db.execute("UPDATE sales_orders SET status = 'INVOICED' WHERE id = ?", (order_id,))
        return new_id
