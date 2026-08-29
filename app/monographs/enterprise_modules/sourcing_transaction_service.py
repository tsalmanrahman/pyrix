from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class SourcingTransactionService:

    # =========================================================================
    # 1. PURCHASE REQUISITIONS (PR)
    # =========================================================================
    @staticmethod
    def get_requisitions(company_id: Optional[str] = None, req_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT r.*, c.name AS company_name, c.short_code AS company_code,
                   d.dept_code, d.dept_name,
                   (SELECT COUNT(*) FROM sourcing_requisition_items i WHERE i.requisition_id = r.id) AS item_count
            FROM sourcing_requisitions r
            JOIN companies c ON r.company_id = c.id
            LEFT JOIN gl_departments d ON r.department_id = d.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND r.company_id = ?"
            params.append(company_id)
        if req_type:
            sql += " AND r.req_type = ?"
            params.append(req_type)
        if status:
            sql += " AND r.status = ?"
            params.append(status)
        sql += " ORDER BY r.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def get_requisition_by_id(req_id: str) -> Optional[Dict[str, Any]]:
        req = db.query_one(
            """
            SELECT r.*, c.name AS company_name, c.short_code AS company_code,
                   d.dept_code, d.dept_name
            FROM sourcing_requisitions r
            JOIN companies c ON r.company_id = c.id
            LEFT JOIN gl_departments d ON r.department_id = d.id
            WHERE r.id = ?
            """,
            (req_id,)
        )
        if req:
            req["items"] = db.query(
                "SELECT * FROM sourcing_requisition_items WHERE requisition_id = ? ORDER BY code ASC",
                (req_id,)
            )
        return req

    @staticmethod
    def create_requisition(
        company_id: str,
        req_number: str,
        req_type: str,
        title: str,
        priority: str,
        requester_name: str,
        notes: Optional[str] = None,
        department_id: Optional[str] = None,
        cost_centre_id: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        req_id = str(uuid.uuid4())
        total_amount = sum(float(it.get("quantity", 1)) * float(it.get("estimated_unit_price", 0)) for it in (items or []))

        db.execute(
            """
            INSERT INTO sourcing_requisitions 
            (id, company_id, req_number, req_type, department_id, cost_centre_id, title, priority, requester_name, total_estimated_amount, currency, status, is_closed, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USD', 'PENDING_APPROVAL', 0, ?)
            """,
            (req_id, company_id, req_number.strip(), req_type, department_id or None, cost_centre_id or None, title.strip(), priority, requester_name.strip(), total_amount, notes)
        )

        for it in (items or []):
            qty = float(it.get("quantity", 1))
            price = float(it.get("estimated_unit_price", 0))
            db.execute(
                """
                INSERT INTO sourcing_requisition_items 
                (requisition_id, item_code, item_name, specification, uom, quantity, estimated_unit_price, estimated_total, required_by_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (req_id, it.get("item_code", "ITM-GEN"), it.get("item_name", "Item"), it.get("specification", ""), it.get("uom", "PCS"), qty, price, qty * price, it.get("required_by_date", "2026-09-30"))
            )

        # Seed tier 1 approval
        db.execute(
            """
            INSERT INTO sourcing_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments)
            VALUES ('PR', ?, 1, 'Tier 1: Department Requester Sign-off', ?, 'Department Head', 'PENDING', 'Submitted for procurement review')
            """,
            (req_id, requester_name)
        )
        return req_id

    @staticmethod
    def toggle_close_requisition(req_id: str, close: bool) -> None:
        new_status = "CLOSED" if close else "APPROVED"
        db.execute(
            "UPDATE sourcing_requisitions SET is_closed = ?, status = ? WHERE id = ?",
            (1 if close else 0, new_status, req_id)
        )

    # =========================================================================
    # 2. REQUEST FOR QUOTATION (RFQ) & BIDDING
    # =========================================================================
    @staticmethod
    def get_rfqs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT rfq.*, c.short_code AS company_code, r.req_number, r.req_type,
                   (SELECT COUNT(*) FROM sourcing_rfq_bids b WHERE b.rfq_id = rfq.id) AS bid_count,
                   (SELECT cs.cs_number FROM sourcing_comparative_statements cs WHERE cs.rfq_id = rfq.id) AS cs_number
            FROM sourcing_rfqs rfq
            JOIN companies c ON rfq.company_id = c.id
            LEFT JOIN sourcing_requisitions r ON rfq.requisition_id = r.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND rfq.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY rfq.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def get_rfq_by_id(rfq_id: str) -> Optional[Dict[str, Any]]:
        rfq = db.query_one(
            """
            SELECT rfq.*, c.name AS company_name, c.short_code AS company_code,
                   r.req_number, r.req_type, r.total_estimated_amount
            FROM sourcing_rfqs rfq
            JOIN companies c ON rfq.company_id = c.id
            LEFT JOIN sourcing_requisitions r ON rfq.requisition_id = r.id
            WHERE rfq.id = ?
            """,
            (rfq_id,)
        )
        if rfq:
            rfq["bids"] = db.query(
                """
                SELECT b.*, v.vendor_code, v.vendor_name, v.rating_stars, v.currency AS vendor_currency
                FROM sourcing_rfq_bids b
                JOIN sourcing_vendors v ON b.vendor_id = v.id
                WHERE b.rfq_id = ?
                ORDER BY b.quoted_amount ASC
                """,
                (rfq_id,)
            )
        return rfq

    @staticmethod
    def create_rfq(
        rfq_number: str,
        company_id: str,
        title: str,
        submission_deadline: str,
        requisition_id: Optional[str] = None
    ) -> str:
        rfq_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_rfqs (id, rfq_number, company_id, requisition_id, title, submission_deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, 'OPEN')
            """,
            (rfq_id, rfq_number.strip(), company_id, requisition_id or None, title.strip(), submission_deadline)
        )
        return rfq_id

    @staticmethod
    def submit_rfq_bid(
        rfq_id: str,
        vendor_id: str,
        bid_reference: str,
        quoted_amount: float,
        delivery_days: int,
        payment_terms: str,
        technical_score: float = 90.0,
        commercial_score: float = 90.0,
        remarks: Optional[str] = None
    ) -> str:
        bid_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_rfq_bids 
            (id, rfq_id, vendor_id, bid_reference, quoted_amount, delivery_days, payment_terms, technical_score, commercial_score, rank_position, is_winner, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?)
            """,
            (bid_id, rfq_id, vendor_id, bid_reference.strip(), quoted_amount, delivery_days, payment_terms.strip(), technical_score, commercial_score, remarks)
        )
        # Update RFQ status
        db.execute("UPDATE sourcing_rfqs SET status = 'BIDS_RECEIVED' WHERE id = ?", (rfq_id,))
        return bid_id

    # =========================================================================
    # 3. COMPARATIVE STATEMENTS (CS) MATRIX & EVALUATION ENGINE
    # =========================================================================
    @staticmethod
    def get_comparative_statements(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT cs.*, rfq.rfq_number, rfq.title AS rfq_title, c.short_code AS company_code,
                   v.vendor_name AS winning_vendor_name, v.vendor_code AS winning_vendor_code,
                   (SELECT COUNT(*) FROM sourcing_rfq_bids b WHERE b.rfq_id = cs.rfq_id) AS total_bids
            FROM sourcing_comparative_statements cs
            JOIN sourcing_rfqs rfq ON cs.rfq_id = rfq.id
            JOIN companies c ON rfq.company_id = c.id
            LEFT JOIN sourcing_vendors v ON cs.winning_vendor_id = v.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND rfq.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY cs.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def get_comparative_statement_by_id(cs_id: str) -> Optional[Dict[str, Any]]:
        cs = db.query_one(
            """
            SELECT cs.*, rfq.rfq_number, rfq.title AS rfq_title, rfq.requisition_id,
                   c.name AS company_name, c.short_code AS company_code,
                   v.vendor_name AS winning_vendor_name, v.vendor_code AS winning_vendor_code
            FROM sourcing_comparative_statements cs
            JOIN sourcing_rfqs rfq ON cs.rfq_id = rfq.id
            JOIN companies c ON rfq.company_id = c.id
            LEFT JOIN sourcing_vendors v ON cs.winning_vendor_id = v.id
            WHERE cs.id = ?
            """,
            (cs_id,)
        )
        if cs:
            cs["bids"] = db.query(
                """
                SELECT b.*, v.vendor_code, v.vendor_name, v.rating_stars, v.country, v.currency AS vendor_currency
                FROM sourcing_rfq_bids b
                JOIN sourcing_vendors v ON b.vendor_id = v.id
                WHERE b.rfq_id = ?
                ORDER BY b.quoted_amount ASC
                """,
                (cs["rfq_id"],)
            )
        return cs

    @staticmethod
    def evaluate_and_generate_cs(rfq_id: str, cs_number: str, evaluated_by: str = "Tender Committee") -> str:
        cs_id = str(uuid.uuid4())
        rfq = db.query_one("SELECT * FROM sourcing_rfqs WHERE id = ?", (rfq_id,))
        bids = db.query("SELECT * FROM sourcing_rfq_bids WHERE rfq_id = ? ORDER BY quoted_amount ASC", (rfq_id,))

        winning_vendor_id = None
        winning_amount = 0.0
        if bids:
            winning_vendor_id = bids[0]["vendor_id"]
            winning_amount = bids[0]["quoted_amount"]
            # Mark winning bid
            db.execute("UPDATE sourcing_rfq_bids SET is_winner = 1, rank_position = 1 WHERE id = ?", (bids[0]["id"],))

        db.execute(
            """
            INSERT INTO sourcing_comparative_statements 
            (id, cs_number, rfq_id, title, winning_vendor_id, winning_amount, evaluation_summary, evaluated_by, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Automated L1 lowest-evaluated responsive bid awarded.', ?, 'APPROVED')
            """,
            (cs_id, cs_number.strip(), rfq_id, f"Comparative Statement: {rfq['title'] if rfq else 'Tender'}", winning_vendor_id, winning_amount, evaluated_by)
        )
        db.execute("UPDATE sourcing_rfqs SET status = 'EVALUATED' WHERE id = ?", (rfq_id,))
        return cs_id

    # =========================================================================
    # 4. PURCHASE ORDERS (PO)
    # =========================================================================
    @staticmethod
    def get_purchase_orders(company_id: Optional[str] = None, po_category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT po.*, c.name AS company_name, c.short_code AS company_code,
                   v.vendor_code, v.vendor_name, v.rating_stars,
                   (SELECT COUNT(*) FROM sourcing_po_items pi WHERE pi.po_id = po.id) AS item_count,
                   (SELECT lc.lc_number FROM sourcing_letters_of_credit lc WHERE lc.po_id = po.id) AS lc_number
            FROM sourcing_purchase_orders po
            JOIN companies c ON po.company_id = c.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        if po_category:
            sql += " AND po.po_category = ?"
            params.append(po_category)
        if status:
            sql += " AND po.status = ?"
            params.append(status)
        sql += " ORDER BY po.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def get_purchase_order_by_id(po_id: str) -> Optional[Dict[str, Any]]:
        po = db.query_one(
            """
            SELECT po.*, c.name AS company_name, c.short_code AS company_code, c.headquarters,
                   v.vendor_code, v.vendor_name, v.address AS vendor_address, v.contact_person, v.email AS vendor_email, v.phone AS vendor_phone, v.bank_name, v.bank_account, v.tax_id_tin, v.vat_bin,
                   r.req_number, cs.cs_number
            FROM sourcing_purchase_orders po
            JOIN companies c ON po.company_id = c.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            LEFT JOIN sourcing_requisitions r ON po.requisition_id = r.id
            LEFT JOIN sourcing_comparative_statements cs ON po.cs_id = cs.id
            WHERE po.id = ?
            """,
            (po_id,)
        )
        if po:
            po["items"] = db.query(
                "SELECT * FROM sourcing_po_items WHERE po_id = ? ORDER BY code ASC",
                (po_id,)
            )
            po["approvals"] = db.query(
                "SELECT * FROM sourcing_approvals WHERE entity_type = 'PO' AND entity_id = ? ORDER BY tier_level ASC",
                (po_id,)
            )
            po["lc"] = db.query_one(
                "SELECT * FROM sourcing_letters_of_credit WHERE po_id = ?",
                (po_id,)
            )
        return po

    @staticmethod
    def create_purchase_order(
        company_id: str,
        po_number: str,
        po_category: str,
        vendor_id: str,
        subtotal: float,
        tax_amount: float = 0.0,
        freight_amount: float = 0.0,
        currency: str = "USD",
        exchange_rate: float = 1.0,
        payment_terms: str = "Net 30 Days",
        incoterm: str = "FOB",
        shipping_address: Optional[str] = None,
        billing_address: Optional[str] = None,
        requisition_id: Optional[str] = None,
        cs_id: Optional[str] = None,
        created_by: str = "Procurement Officer",
        items: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        po_id = str(uuid.uuid4())
        total_amount = subtotal + tax_amount + freight_amount

        db.execute(
            """
            INSERT INTO sourcing_purchase_orders 
            (id, company_id, po_number, po_category, vendor_id, requisition_id, cs_id, currency, exchange_rate, subtotal, tax_amount, freight_amount, total_amount, payment_terms, incoterm, shipping_address, billing_address, status, current_approval_tier, max_approval_tier, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_APPROVAL', 1, 3, ?)
            """,
            (po_id, company_id, po_number.strip(), po_category, vendor_id, requisition_id or None, cs_id or None, currency, exchange_rate, subtotal, tax_amount, freight_amount, total_amount, payment_terms, incoterm, shipping_address, billing_address, created_by)
        )

        for it in (items or []):
            qty = float(it.get("quantity", 1))
            price = float(it.get("unit_price", 0))
            db.execute(
                """
                INSERT INTO sourcing_po_items (po_id, item_code, item_name, uom, quantity, unit_price, line_total, received_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0.0)
                """,
                (po_id, it.get("item_code", "ITM-PO"), it.get("item_name", "Item"), it.get("uom", "PCS"), qty, price, qty * price)
            )

        # Seed 3 tiers of approvals
        db.execute(
            """
            INSERT INTO sourcing_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments)
            VALUES ('PO', ?, 1, 'Tier 1: Department Requester Approval', ?, 'Department Head', 'PENDING', 'PO created and queued for initial verification')
            """,
            (po_id, created_by)
        )
        return po_id

    @staticmethod
    def generate_po_from_cs_winner(cs_id: str, po_number: str, po_category: str = "IMPORT_WITH_PR", created_by: str = "Procurement Officer") -> str:
        cs = db.query_one(
            """
            SELECT cs.*, rfq.company_id, rfq.requisition_id, rfq.title AS rfq_title
            FROM sourcing_comparative_statements cs
            JOIN sourcing_rfqs rfq ON cs.rfq_id = rfq.id
            WHERE cs.id = ?
            """,
            (cs_id,)
        )
        if not cs or not cs["winning_vendor_id"]:
            raise ValueError("Comparative statement or winner not found.")

        # Get winning bid items/amount
        winning_bid = db.query_one(
            "SELECT * FROM sourcing_rfq_bids WHERE rfq_id = ? AND vendor_id = ?",
            (cs["rfq_id"], cs["winning_vendor_id"])
        )
        amount = winning_bid["quoted_amount"] if winning_bid else (cs["winning_amount"] or 10000.0)
        pay_terms = winning_bid["payment_terms"] if winning_bid else "Net 45 Days Credit"

        # Fetch PR items if available
        pr_items = []
        if cs["requisition_id"]:
            pr_items = db.query("SELECT * FROM sourcing_requisition_items WHERE requisition_id = ?", (cs["requisition_id"],))

        items = []
        if pr_items:
            for p in pr_items:
                items.append({
                    "item_code": p["item_code"],
                    "item_name": p["item_name"],
                    "uom": p["uom"],
                    "quantity": p["quantity"],
                    "unit_price": p["estimated_unit_price"]
                })
        else:
            items.append({
                "item_code": "ITM-CS-001",
                "item_name": cs["rfq_title"],
                "uom": "LOT",
                "quantity": 1.0,
                "unit_price": amount
            })

        po_id = SourcingTransactionService.create_purchase_order(
            company_id=cs["company_id"],
            po_number=po_number,
            po_category=po_category,
            vendor_id=cs["winning_vendor_id"],
            subtotal=amount,
            tax_amount=0.0,
            freight_amount=0.0,
            currency="USD",
            payment_terms=pay_terms,
            incoterm="FOB",
            requisition_id=cs["requisition_id"],
            cs_id=cs_id,
            created_by=created_by,
            items=items
        )

        db.execute("UPDATE sourcing_comparative_statements SET status = 'PO_AWARDED' WHERE id = ?", (cs_id,))
        return po_id

    @staticmethod
    def close_or_cancel_po(po_id: str, action_status: str = "CANCELLED", reason: Optional[str] = None) -> None:
        db.execute("UPDATE sourcing_purchase_orders SET status = ? WHERE id = ?", (action_status, po_id))

    # =========================================================================
    # 5. GOODS RETURN NOTES (GRN RETURN)
    # =========================================================================
    @staticmethod
    def get_goods_returns(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT gr.*, po.po_number, po.currency, c.short_code AS company_code,
                   v.vendor_name, v.vendor_code
            FROM sourcing_goods_returns gr
            JOIN sourcing_purchase_orders po ON gr.po_id = po.id
            JOIN companies c ON po.company_id = c.id
            JOIN sourcing_vendors v ON gr.vendor_id = v.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY gr.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def create_goods_return(
        po_id: str,
        vendor_id: str,
        return_number: str,
        return_date: str,
        reason: str,
        total_returned_value: float
    ) -> str:
        gr_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_goods_returns 
            (id, return_number, po_id, vendor_id, return_date, reason, total_returned_value, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ISSUED')
            """,
            (gr_id, return_number.strip(), po_id, vendor_id, return_date, reason.strip(), total_returned_value)
        )
        return gr_id
