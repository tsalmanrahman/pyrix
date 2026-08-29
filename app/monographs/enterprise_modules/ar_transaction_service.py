from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.db import db

class ARTransactionService:

    # =========================================================================
    # 1. Adjustment of Advance with Bills
    # =========================================================================
    @staticmethod
    def get_advance_adjustments(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code
                FROM ar_advance_adjustments a
                JOIN ar_customers c ON a.customer_id = c.id
                JOIN companies comp ON a.company_id = comp.id
                WHERE a.company_id = ? AND COALESCE(a.isDelete, 0) = 0
                ORDER BY a.adjustment_date DESC, a.voucher_number DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code
            FROM ar_advance_adjustments a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN companies comp ON a.company_id = comp.id
            WHERE COALESCE(a.isDelete, 0) = 0
            ORDER BY a.adjustment_date DESC, a.voucher_number DESC
            """
        )

    @staticmethod
    def create_advance_adjustment(
        voucher_number: str,
        adjustment_date: str,
        company_id: str,
        customer_id: str,
        advance_ref_number: str,
        invoice_number: str,
        original_advance_amount: float,
        adjusted_amount: float,
        unadjusted_balance: float,
        narration: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_advance_adjustments (
                voucher_number, adjustment_date, company_id, customer_id,
                advance_ref_number, invoice_number, original_advance_amount,
                adjusted_amount, unadjusted_balance, narration, status, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'POSTED', 0)
            """,
            (
                voucher_number.strip(), adjustment_date, company_id, customer_id,
                advance_ref_number.strip(), invoice_number.strip(), original_advance_amount,
                adjusted_amount, unadjusted_balance, narration.strip() if narration else None
            )
        )
        # Update customer balance
        db.execute(
            "UPDATE ar_customers SET current_balance = current_balance - ? WHERE id = ?",
            (adjusted_amount, customer_id)
        )

    @staticmethod
    def delete_advance_adjustment(adjustment_id: str) -> None:
        db.execute("UPDATE ar_advance_adjustments SET isDelete = 1 WHERE id = ?", (adjustment_id,))

    # =========================================================================
    # 2. Adjustment of Accounts Receivable (General Adjustments)
    # =========================================================================
    @staticmethod
    def get_general_adjustments(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT a.*, c.customer_code, c.customer_name, t.adjustment_code, t.adjustment_name,
                       comp.short_code AS company_code, g.account_number AS offset_gl_num
                FROM ar_general_adjustments a
                JOIN ar_customers c ON a.customer_id = c.id
                JOIN ar_adjustment_types t ON a.adjustment_type_id = t.id
                JOIN companies comp ON a.company_id = comp.id
                LEFT JOIN gl_accounts g ON a.offset_gl_account_id = g.id
                WHERE a.company_id = ? AND COALESCE(a.isDelete, 0) = 0
                ORDER BY a.adjustment_date DESC, a.voucher_number DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT a.*, c.customer_code, c.customer_name, t.adjustment_code, t.adjustment_name,
                   comp.short_code AS company_code, g.account_number AS offset_gl_num
            FROM ar_general_adjustments a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN ar_adjustment_types t ON a.adjustment_type_id = t.id
            JOIN companies comp ON a.company_id = comp.id
            LEFT JOIN gl_accounts g ON a.offset_gl_account_id = g.id
            WHERE COALESCE(a.isDelete, 0) = 0
            ORDER BY a.adjustment_date DESC, a.voucher_number DESC
            """
        )

    @staticmethod
    def create_general_adjustment(
        voucher_number: str,
        adjustment_date: str,
        company_id: str,
        customer_id: str,
        adjustment_type_id: str,
        adjustment_category: str,
        amount: float,
        reason_description: str,
        offset_gl_account_id: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_general_adjustments (
                voucher_number, adjustment_date, company_id, customer_id,
                adjustment_type_id, adjustment_category, amount, reason_description,
                offset_gl_account_id, approved_by, status, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Financial Controller', 'APPROVED', 0)
            """,
            (
                voucher_number.strip(), adjustment_date, company_id, customer_id,
                adjustment_type_id, adjustment_category.strip(), amount,
                reason_description.strip(), offset_gl_account_id if offset_gl_account_id else None
            )
        )
        # Update customer balance (+ for DEBIT adjustment, - for CREDIT adjustment)
        if adjustment_category == "DEBIT":
            db.execute("UPDATE ar_customers SET current_balance = current_balance + ? WHERE id = ?", (amount, customer_id))
        else:
            db.execute("UPDATE ar_customers SET current_balance = current_balance - ? WHERE id = ?", (amount, customer_id))

    @staticmethod
    def delete_general_adjustment(adjustment_id: str) -> None:
        db.execute("UPDATE ar_general_adjustments SET isDelete = 1 WHERE id = ?", (adjustment_id,))

    # =========================================================================
    # 3 & 4. Debit Notes (With & Without Invoice Reference)
    # =========================================================================
    @staticmethod
    def get_debit_notes_with_ref(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND a.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code,
                   g.account_number AS gl_num, g.account_name AS gl_name
            FROM ar_notes a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN companies comp ON a.company_id = comp.id
            LEFT JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE a.note_type = 'DEBIT_WITH_REF' AND COALESCE(a.isDelete, 0) = 0 {filter_sql}
            ORDER BY a.note_date DESC, a.note_number DESC
            """,
            params
        )

    @staticmethod
    def get_debit_notes_direct(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND a.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code,
                   g.account_number AS gl_num, g.account_name AS gl_name
            FROM ar_notes a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN companies comp ON a.company_id = comp.id
            LEFT JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE a.note_type = 'DEBIT_DIRECT' AND COALESCE(a.isDelete, 0) = 0 {filter_sql}
            ORDER BY a.note_date DESC, a.note_number DESC
            """,
            params
        )

    # =========================================================================
    # 5 & 6. Credit Notes (With & Without Invoice Reference)
    # =========================================================================
    @staticmethod
    def get_credit_notes_with_ref(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND a.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code,
                   g.account_number AS gl_num, g.account_name AS gl_name
            FROM ar_notes a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN companies comp ON a.company_id = comp.id
            LEFT JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE a.note_type = 'CREDIT_WITH_REF' AND COALESCE(a.isDelete, 0) = 0 {filter_sql}
            ORDER BY a.note_date DESC, a.note_number DESC
            """,
            params
        )

    @staticmethod
    def get_credit_notes_direct(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND a.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT a.*, c.customer_code, c.customer_name, comp.short_code AS company_code,
                   g.account_number AS gl_num, g.account_name AS gl_name
            FROM ar_notes a
            JOIN ar_customers c ON a.customer_id = c.id
            JOIN companies comp ON a.company_id = comp.id
            LEFT JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE a.note_type = 'CREDIT_DIRECT' AND COALESCE(a.isDelete, 0) = 0 {filter_sql}
            ORDER BY a.note_date DESC, a.note_number DESC
            """,
            params
        )

    @staticmethod
    def create_note(
        note_number: str,
        note_type: str,
        note_date: str,
        company_id: str,
        customer_id: str,
        note_amount: float,
        tax_amount: float,
        reason: str,
        invoice_ref_number: Optional[str] = None,
        original_invoice_amount: Optional[float] = None,
        gl_account_id: Optional[str] = None
    ) -> None:
        total_amount = note_amount + tax_amount
        db.execute(
            """
            INSERT INTO ar_notes (
                note_number, note_type, note_date, company_id, customer_id,
                invoice_ref_number, original_invoice_amount, note_amount, tax_amount,
                total_amount, reason, gl_account_id, status, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'POSTED', 0)
            """,
            (
                note_number.strip(), note_type.strip(), note_date, company_id, customer_id,
                invoice_ref_number.strip() if invoice_ref_number else None,
                original_invoice_amount, note_amount, tax_amount, total_amount,
                reason.strip(), gl_account_id if gl_account_id else None
            )
        )
        # Debit notes increase receivable balance, Credit notes decrease receivable balance
        if "DEBIT" in note_type:
            db.execute("UPDATE ar_customers SET current_balance = current_balance + ? WHERE id = ?", (total_amount, customer_id))
        else:
            db.execute("UPDATE ar_customers SET current_balance = current_balance - ? WHERE id = ?", (total_amount, customer_id))

    @staticmethod
    def delete_note(note_id: str) -> None:
        db.execute("UPDATE ar_notes SET isDelete = 1 WHERE id = ?", (note_id,))

    # =========================================================================
    # 7. Issue Money Receipts (Active Receipts)
    # =========================================================================
    @staticmethod
    def get_active_money_receipts(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND r.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT r.*, c.customer_code, c.customer_name, comp.short_code AS company_code
            FROM ar_money_receipts r
            JOIN ar_customers c ON r.customer_id = c.id
            JOIN companies comp ON r.company_id = comp.id
            WHERE r.status = 'CLEARED' AND COALESCE(r.isDelete, 0) = 0 {filter_sql}
            ORDER BY r.receipt_date DESC, r.receipt_number DESC
            """,
            params
        )

    @staticmethod
    def issue_money_receipt(
        receipt_number: str,
        receipt_date: str,
        company_id: str,
        customer_id: str,
        payment_mode: str,
        receipt_amount: float,
        instrument_ref: Optional[str] = None,
        instrument_date: Optional[str] = None,
        allocated_invoices: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_money_receipts (
                receipt_number, receipt_date, company_id, customer_id,
                payment_mode, instrument_ref, instrument_date, receipt_amount,
                allocated_invoices, remarks, status, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CLEARED', 0)
            """,
            (
                receipt_number.strip(), receipt_date, company_id, customer_id,
                payment_mode.strip(), instrument_ref.strip() if instrument_ref else None,
                instrument_date if instrument_date else None, receipt_amount,
                allocated_invoices.strip() if allocated_invoices else None,
                remarks.strip() if remarks else None
            )
        )
        # Decrease customer receivable balance upon payment receipt
        db.execute("UPDATE ar_customers SET current_balance = current_balance - ? WHERE id = ?", (receipt_amount, customer_id))

    # =========================================================================
    # 8. Cancel Money Receipts (Audit Void & Cancellation)
    # =========================================================================
    @staticmethod
    def get_cancelled_money_receipts(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filter_sql = "AND r.company_id = ?" if company_id else ""
        params = (company_id,) if company_id else ()
        return db.query(
            f"""
            SELECT r.*, c.customer_code, c.customer_name, comp.short_code AS company_code
            FROM ar_money_receipts r
            JOIN ar_customers c ON r.customer_id = c.id
            JOIN companies comp ON r.company_id = comp.id
            WHERE r.status = 'CANCELLED' {filter_sql}
            ORDER BY r.cancelled_at DESC, r.receipt_number DESC
            """,
            params
        )

    @staticmethod
    def cancel_money_receipt(receipt_id: str, cancelled_reason: str) -> None:
        receipt = db.query_one("SELECT * FROM ar_money_receipts WHERE id = ?", (receipt_id,))
        if receipt and receipt["status"] != "CANCELLED":
            db.execute(
                """
                UPDATE ar_money_receipts
                SET status = 'CANCELLED', cancelled_at = GETDATE(), 
                    cancelled_reason = ?, isDelete = 1
                WHERE id = ?
                """,
                (cancelled_reason.strip(), receipt_id)
            )
            # Reverse customer balance (re-instate receivable)
            db.execute(
                "UPDATE ar_customers SET current_balance = current_balance + ? WHERE id = ?",
                (receipt["receipt_amount"], receipt["customer_id"])
            )
