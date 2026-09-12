from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.core.db import db

class GLJournalService:

    # =========================================================================
    # 1. Journal Vouchers (Double-Entry Balanced Transactions)
    # =========================================================================
    @staticmethod
    def get_vouchers_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT v.*, b.batch_number, b.batch_title, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM gl_journal_voucher_lines l WHERE l.voucher_id = v.id) AS line_count
            FROM gl_journal_vouchers v
            LEFT JOIN gl_journal_batches b ON v.batch_id = b.id
            JOIN companies c ON v.company_id = c.id
            WHERE v.company_id = ? AND COALESCE(v.isDelete, 0) = 0
            ORDER BY v.voucher_date DESC, v.created_at DESC
            """,
            (company_id,)
        )

    @staticmethod
    def get_voucher_by_id(voucher_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT v.*, b.batch_number, b.batch_title, c.name AS company_name, c.short_code AS company_code,
                   COALESCE(v.currency, c.currency, 'BDT') AS currency,
                   COALESCE(v.exchange_rate, 1.0) AS exchange_rate,
                   v.fiscal_year, v.fiscal_period
            FROM gl_journal_vouchers v
            LEFT JOIN gl_journal_batches b ON v.batch_id = b.id
            JOIN companies c ON v.company_id = c.id
            WHERE v.id = ? AND COALESCE(v.isDelete, 0) = 0
            """,
            (voucher_id,)
        )

    @staticmethod
    def get_voucher_lines(voucher_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT l.*, a.account_number, a.account_name, a.account_type,
                   sa.sub_account_code, sa.sub_account_name,
                   cc.cost_center_code AS cost_centre_code, cc.name AS cost_centre_name,
                   d.dept_code, d.dept_name
            FROM gl_journal_voucher_lines l
            JOIN gl_accounts a ON l.gl_account_id = a.id
            LEFT JOIN gl_sub_accounts sa ON l.sub_account_id = sa.id
            LEFT JOIN admin_cost_centers cc ON l.cost_centre_id = cc.id
            LEFT JOIN gl_departments d ON l.department_id = d.id
            WHERE l.voucher_id = ?
            ORDER BY l.sort_order ASC, l.debit_amount DESC
            """,
            (voucher_id,)
        )

    @staticmethod
    def get_all_sub_accounts(gl_account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if gl_account_id:
            return db.query(
                """
                SELECT sa.*, a.account_number, a.account_name
                FROM gl_sub_accounts sa
                JOIN gl_accounts a ON sa.gl_account_id = a.id
                WHERE sa.gl_account_id = ? AND COALESCE(sa.isDelete, 0) = 0 AND COALESCE(sa.is_active, 1) = 1
                ORDER BY sa.sub_account_code ASC
                """,
                (gl_account_id,)
            )
        return db.query(
            """
            SELECT sa.*, a.account_number, a.account_name
            FROM gl_sub_accounts sa
            JOIN gl_accounts a ON sa.gl_account_id = a.id
            WHERE COALESCE(sa.isDelete, 0) = 0 AND COALESCE(sa.is_active, 1) = 1
            ORDER BY sa.sub_account_code ASC
            """
        )

    @staticmethod
    def get_fiscal_periods() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM admin_fiscal_periods ORDER BY start_date ASC")

    @staticmethod
    def create_journal_voucher(
        company_id: str,
        voucher_number: str,
        voucher_date: str,
        reference_number: str,
        narration: str,
        lines: List[Dict[str, Any]],
        status: str = "POSTED",
        batch_id: Optional[str] = None,
        currency: str = "BDT",
        exchange_rate: float = 1.0,
        fiscal_year: Optional[str] = None,
        fiscal_period: Optional[int] = None,
        created_by: str = "Operator Admin"
    ) -> str:
        total_amount = sum(float(line.get("debit_amount", 0.0) or 0.0) for line in lines)
        
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO gl_journal_vouchers (
                    voucher_number, batch_id, company_id, voucher_date, reference_number,
                    narration, total_amount, status, currency, exchange_rate, fiscal_year,
                    fiscal_period, created_by, isDelete
                )
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    voucher_number.strip(),
                    batch_id if batch_id else None,
                    company_id,
                    voucher_date,
                    reference_number.strip() if reference_number else None,
                    narration.strip(),
                    total_amount,
                    status,
                    currency,
                    float(exchange_rate or 1.0),
                    fiscal_year,
                    int(fiscal_period) if fiscal_period else None,
                    created_by
                )
            )
            voucher_id = str(cursor.fetchone()[0])

            for idx, line in enumerate(lines, start=1):
                cursor.execute(
                    """
                    INSERT INTO gl_journal_voucher_lines (
                        voucher_id, gl_account_id, sub_account_id, cost_centre_id,
                        department_id, project_code, job_id, line_narration,
                        debit_amount, credit_amount, sort_order
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        voucher_id,
                        line["gl_account_id"],
                        line.get("sub_account_id") if line.get("sub_account_id") else None,
                        line.get("cost_centre_id") if line.get("cost_centre_id") else None,
                        line.get("department_id") if line.get("department_id") else None,
                        line.get("project_code") if line.get("project_code") else None,
                        line.get("job_id") if line.get("job_id") else None,
                        line.get("line_narration", "").strip(),
                        float(line.get("debit_amount", 0.0) or 0.0),
                        float(line.get("credit_amount", 0.0) or 0.0),
                        idx
                    )
                )
        return voucher_id

    @staticmethod
    def update_journal_voucher(
        voucher_id: str,
        voucher_date: str,
        reference_number: str,
        narration: str,
        lines: List[Dict[str, Any]],
        status: str = "POSTED",
        currency: str = "BDT",
        exchange_rate: float = 1.0,
        fiscal_year: Optional[str] = None,
        fiscal_period: Optional[int] = None
    ) -> None:
        total_amount = sum(float(line.get("debit_amount", 0.0) or 0.0) for line in lines)

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE gl_journal_vouchers
                SET voucher_date = ?, reference_number = ?, narration = ?, total_amount = ?,
                    status = ?, currency = ?, exchange_rate = ?, fiscal_year = ?, fiscal_period = ?
                WHERE id = ?
                """,
                (
                    voucher_date,
                    reference_number.strip() if reference_number else None,
                    narration.strip(),
                    total_amount,
                    status,
                    currency,
                    float(exchange_rate or 1.0),
                    fiscal_year,
                    int(fiscal_period) if fiscal_period else None,
                    voucher_id
                )
            )
            # Recreate lines
            cursor.execute("DELETE FROM gl_journal_voucher_lines WHERE voucher_id = ?", (voucher_id,))
            for idx, line in enumerate(lines, start=1):
                cursor.execute(
                    """
                    INSERT INTO gl_journal_voucher_lines (
                        voucher_id, gl_account_id, sub_account_id, cost_centre_id,
                        department_id, project_code, job_id, line_narration,
                        debit_amount, credit_amount, sort_order
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        voucher_id,
                        line["gl_account_id"],
                        line.get("sub_account_id") if line.get("sub_account_id") else None,
                        line.get("cost_centre_id") if line.get("cost_centre_id") else None,
                        line.get("department_id") if line.get("department_id") else None,
                        line.get("project_code") if line.get("project_code") else None,
                        line.get("job_id") if line.get("job_id") else None,
                        line.get("line_narration", "").strip(),
                        float(line.get("debit_amount", 0.0) or 0.0),
                        float(line.get("credit_amount", 0.0) or 0.0),
                        idx
                    )
                )

    @staticmethod
    def delete_journal_voucher(voucher_id: str) -> bool:
        try:
            valid_uuid = str(uuid.UUID(str(voucher_id)))
            db.execute("UPDATE gl_journal_vouchers SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (valid_uuid,))
            return True
        except (ValueError, Exception):
            return False

    # =========================================================================
    # 2. Journal Batches & Processing Lifecycle
    # =========================================================================
    @staticmethod
    def get_batches_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM gl_journal_vouchers v WHERE v.batch_id = b.id AND COALESCE(v.isDelete, 0) = 0) AS voucher_count
            FROM gl_journal_batches b
            JOIN companies c ON b.company_id = c.id
            WHERE b.company_id = ? AND COALESCE(b.isDelete, 0) = 0
            ORDER BY b.created_at DESC
            """,
            (company_id,)
        )

    @staticmethod
    def get_batch_by_id(batch_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT b.*, c.name AS company_name, c.short_code AS company_code
            FROM gl_journal_batches b
            JOIN companies c ON b.company_id = c.id
            WHERE b.id = ? AND COALESCE(b.isDelete, 0) = 0
            """,
            (batch_id,)
        )

    @staticmethod
    def post_batch(batch_id: str) -> bool:
        db.execute("UPDATE gl_journal_batches SET status = 'POSTED' WHERE id = ?", (batch_id,))
        db.execute("UPDATE gl_journal_vouchers SET status = 'POSTED' WHERE batch_id = ?", (batch_id,))
        return True

    @staticmethod
    def unpost_batch(batch_id: str) -> bool:
        db.execute("UPDATE gl_journal_batches SET status = 'UNPOSTED' WHERE id = ?", (batch_id,))
        db.execute("UPDATE gl_journal_vouchers SET status = 'UNPOSTED' WHERE batch_id = ?", (batch_id,))
        return True

    @staticmethod
    def delete_batch(batch_id: str) -> bool:
        try:
            valid_uuid = str(uuid.UUID(str(batch_id)))
            db.execute("UPDATE gl_journal_batches SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (valid_uuid,))
            return True
        except (ValueError, Exception):
            return False

    # =========================================================================
    # 3. Batch Templates & Template Batch Generation Wizard
    # =========================================================================
    @staticmethod
    def get_templates_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT t.*, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM gl_batch_template_lines l WHERE l.template_id = t.id) AS line_count
            FROM gl_batch_templates t
            JOIN companies c ON t.company_id = c.id
            WHERE t.company_id = ? AND COALESCE(t.isDelete, 0) = 0
            ORDER BY t.created_at DESC
            """,
            (company_id,)
        )

    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM gl_batch_templates WHERE id = ? AND COALESCE(isDelete, 0) = 0", (template_id,))

    @staticmethod
    def get_template_lines(template_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT l.*, a.account_number, a.account_name, 
                   cc.cost_center_code AS cost_centre_code, cc.name AS cost_centre_name
            FROM gl_batch_template_lines l
            JOIN gl_accounts a ON l.gl_account_id = a.id
            LEFT JOIN admin_cost_centers cc ON l.cost_centre_id = cc.id
            WHERE l.template_id = ?
            ORDER BY l.id ASC
            """,
            (template_id,)
        )

    @staticmethod
    def generate_batch_from_template(
        company_id: str,
        template_id: str,
        batch_title: str,
        amount: float = 50000.0,
        is_reversal: bool = False,
        fiscal_year: Optional[str] = None,
        fiscal_period: Optional[int] = None,
        created_by: str = "Operator Admin"
    ) -> str:
        template = GLJournalService.get_template_by_id(template_id)
        if not template:
            raise ValueError("Template not found")
        
        lines = GLJournalService.get_template_lines(template_id)
        if not lines:
            raise ValueError("Template has no configured lines")

        batch_number = f"BAT-TMPL-{uuid.uuid4().hex[:6].upper()}"
        reversal_prefix = "[Reversal] " if is_reversal else ""
        final_title = f"{reversal_prefix}{batch_title or f'Generated Batch: {template['template_name']}'}"

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO gl_journal_batches (batch_number, batch_title, company_id, batch_type, total_debit, total_credit, status, created_by, isDelete)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, 'TEMPLATE', ?, ?, 'UNPOSTED', ?, 0)
                """,
                (batch_number, final_title, company_id, amount, amount, created_by)
            )
            batch_id = str(cursor.fetchone()[0])

            # Create voucher under batch
            voucher_number = f"JV-{uuid.uuid4().hex[:6].upper()}"
            cursor.execute(
                """
                INSERT INTO gl_journal_vouchers (
                    voucher_number, batch_id, company_id, voucher_date, reference_number,
                    narration, total_amount, status, created_by, isDelete, fiscal_year, fiscal_period
                )
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, GETDATE(), ?, ?, ?, 'UNPOSTED', ?, 0, ?, ?)
                """,
                (
                    voucher_number,
                    batch_id,
                    company_id,
                    template["template_code"],
                    f"{reversal_prefix}Auto-generated voucher from template {template['template_name']}",
                    amount,
                    created_by,
                    fiscal_year or "2026-2027",
                    fiscal_period or 1
                )
            )
            voucher_id = str(cursor.fetchone()[0])

            for idx, tl in enumerate(lines, start=1):
                orig_is_debit = tl["default_entry_type"] == "DEBIT"
                # If reversal, swap debit and credit
                if is_reversal:
                    debit = 0.0 if orig_is_debit else amount
                    credit = amount if orig_is_debit else 0.0
                else:
                    debit = amount if orig_is_debit else 0.0
                    credit = 0.0 if orig_is_debit else amount

                cursor.execute(
                    """
                    INSERT INTO gl_journal_voucher_lines (voucher_id, gl_account_id, cost_centre_id, line_narration, debit_amount, credit_amount, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (voucher_id, tl["gl_account_id"], tl["cost_centre_id"], f"{reversal_prefix}{tl['default_narration']}", debit, credit, idx)
                )

        return batch_id

    @staticmethod
    def create_template_from_batch(company_id: str, template_name: str, description: str, source_batch_id: str) -> str:
        batch = GLJournalService.get_batch_by_id(source_batch_id)
        if not batch:
            raise ValueError("Source batch not found")

        template_code = f"TMPL-{uuid.uuid4().hex[:5].upper()}"

        lines = db.query("""
            SELECT l.gl_account_id, l.cost_centre_id, l.line_narration,
                   SUM(l.debit_amount) as total_debit,
                   SUM(l.credit_amount) as total_credit
            FROM gl_journal_voucher_lines l
            JOIN gl_journal_vouchers v ON l.voucher_id = v.id
            WHERE v.batch_id = ? AND COALESCE(v.isDelete, 0) = 0
            GROUP BY l.gl_account_id, l.cost_centre_id, l.line_narration
        """, (source_batch_id,))

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO gl_batch_templates (template_code, template_name, company_id, description, is_active, isDelete, created_at)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, 1, 0, GETDATE())
            """, (template_code, template_name.strip(), company_id, description.strip() if description else f"Template created from batch {batch['batch_number']}"))
            template_id = str(cursor.fetchone()[0])

            for idx, line in enumerate(lines, start=1):
                entry_type = "DEBIT" if (line["total_debit"] or 0) >= (line["total_credit"] or 0) else "CREDIT"
                cursor.execute("""
                    INSERT INTO gl_batch_template_lines (template_id, gl_account_id, cost_centre_id, default_entry_type, default_percentage, default_narration)
                    VALUES (?, ?, ?, ?, 100.0, ?)
                """, (template_id, line["gl_account_id"], line["cost_centre_id"], entry_type, line.get("line_narration") or f"Line {idx}"))

        return template_id

    @staticmethod
    def get_auto_profile_preview_lines(profile_id: str) -> List[Dict[str, Any]]:
        profile = db.query_one("SELECT * FROM gl_auto_batch_profiles WHERE id = ? AND COALESCE(isDelete, 0) = 0", (profile_id,))
        if not profile:
            return []
        
        amount = float(profile.get("default_amount") or 12400.0)
        
        if profile.get("template_id"):
            tmpl_lines = GLJournalService.get_template_lines(str(profile["template_id"]))
            if tmpl_lines:
                preview = []
                for tl in tmpl_lines:
                    is_deb = (tl.get("default_entry_type") or "DEBIT") == "DEBIT"
                    preview.append({
                        "account_code": tl.get("account_number", "6010000"),
                        "account_title": tl.get("account_name", "General Operating Account"),
                        "debit_amount": amount if is_deb else 0.0,
                        "credit_amount": 0.0 if is_deb else amount
                    })
                return preview

        # Default fallback lines based on profile code/name
        p_code = (profile.get("profile_code") or "").upper()
        if "DEP" in p_code:
            return [
                {"account_code": "6010001", "account_title": "Depreciation Expense - Machinery & Plant", "debit_amount": round(amount * 0.68, 3), "credit_amount": 0.0},
                {"account_code": "6010002", "account_title": "Depreciation Expense - Motor Vehicles", "debit_amount": round(amount * 0.32, 3), "credit_amount": 0.0},
                {"account_code": "1080001", "account_title": "Accumulated Depreciation - Machinery", "debit_amount": 0.0, "credit_amount": round(amount * 0.68, 3)},
                {"account_code": "1080002", "account_title": "Accumulated Depreciation - Motor Vehicles", "debit_amount": 0.0, "credit_amount": round(amount * 0.32, 3)},
            ]
        else:
            return [
                {"account_code": "6020001", "account_title": "Office Rent & Premises Maintenance", "debit_amount": amount, "credit_amount": 0.0},
                {"account_code": "2010002", "account_title": "Accrued Expenses & Provisions", "debit_amount": 0.0, "credit_amount": amount}
            ]

    @staticmethod
    def bulk_post_batches(batch_ids: List[str]) -> int:
        count = 0
        for bid in batch_ids:
            if bid and str(bid).strip():
                GLJournalService.post_batch(str(bid).strip())
                count += 1
        return count

    # =========================================================================
    # 4. Automatic Batch Profiles & Recurring Auto-Journals Engine
    # =========================================================================
    @staticmethod
    def get_auto_profiles_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query("""
            SELECT p.*, t.template_name, t.template_code
            FROM gl_auto_batch_profiles p
            LEFT JOIN gl_batch_templates t ON p.template_id = t.id
            WHERE (p.company_id = ? OR p.company_id IS NULL) AND COALESCE(p.isDelete, 0) = 0
            ORDER BY p.profile_code ASC
        """, (company_id,))

    @staticmethod
    def create_auto_profile(
        profile_code: str,
        profile_name: str,
        frequency: str,
        day_of_period: int,
        company_id: str,
        template_id: Optional[str],
        default_amount: float,
        is_auto_trigger: bool,
        description: str
    ) -> str:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO gl_auto_batch_profiles (
                    profile_code, profile_name, frequency, day_of_period, company_id,
                    template_id, default_amount, is_auto_trigger, description, isDelete
                ) OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (profile_code.strip(), profile_name.strip(), frequency, day_of_period, company_id, template_id if template_id else None, default_amount, 1 if is_auto_trigger else 0, description.strip()))
            return str(cursor.fetchone()[0])

    @staticmethod
    def delete_auto_profile(profile_id: str) -> bool:
        db.execute("UPDATE gl_auto_batch_profiles SET isDelete = 1 WHERE id = ?", (profile_id,))
        return True

    @staticmethod
    def generate_auto_journals_batch(company_id: str, batch_title: str = "System Automated Accruals & Depreciation Batch", created_by: str = "System Automation") -> str:
        accounts = db.query("SELECT * FROM gl_accounts WHERE COALESCE(isDelete, 0) = 0 ORDER BY account_number ASC")
        if len(accounts) < 2:
            raise ValueError("Insufficient GL accounts for auto batch")

        acc_exp = next((a for a in accounts if a["account_type"] == "EXPENSE"), accounts[0])
        acc_ast = next((a for a in accounts if a["account_type"] == "ASSET"), accounts[1])

        batch_number = f"BAT-AUTO-{uuid.uuid4().hex[:6].upper()}"
        amount = 18500.00

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO gl_journal_batches (batch_number, batch_title, company_id, batch_type, total_debit, total_credit, status, created_by, isDelete)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, 'AUTO', ?, ?, 'UNPOSTED', ?, 0)
                """,
                (batch_number, batch_title, company_id, amount, amount, created_by)
            )
            batch_id = str(cursor.fetchone()[0])

            voucher_number = f"JV-AUTO-{uuid.uuid4().hex[:6].upper()}"
            cursor.execute(
                """
                INSERT INTO gl_journal_vouchers (voucher_number, batch_id, company_id, voucher_date, reference_number, narration, total_amount, status, created_by, isDelete)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, GETDATE(), 'AUTO-REC-2026', 'Automated Periodic Depreciation & Amortization Posting', ?, 'UNPOSTED', ?, 0)
                """,
                (voucher_number, batch_id, company_id, amount, created_by)
            )
            voucher_id = str(cursor.fetchone()[0])

            cursor.execute(
                """
                INSERT INTO gl_journal_voucher_lines (voucher_id, gl_account_id, line_narration, debit_amount, credit_amount, sort_order)
                VALUES (?, ?, 'Automated Plant & Machinery Depreciation Expense', ?, 0.0, 1)
                """,
                (voucher_id, acc_exp["id"], amount)
            )
            cursor.execute(
                """
                INSERT INTO gl_journal_voucher_lines (voucher_id, gl_account_id, line_narration, debit_amount, credit_amount, sort_order)
                VALUES (?, ?, 'Accumulated Fixed Assets Amortization Reserve', 0.0, ?, 2)
                """,
                (voucher_id, acc_ast["id"], amount)
            )

        return batch_id

    # =========================================================================
    # 5. Printable Journal Voucher Document Payload Generator
    # =========================================================================
    @staticmethod
    def get_printable_journal_voucher(voucher_id: str) -> Dict[str, Any]:
        voucher = GLJournalService.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Journal voucher {voucher_id} not found")

        lines = GLJournalService.get_voucher_lines(voucher_id)
        total_debit = sum(float(l["debit_amount"] or 0.0) for l in lines)
        total_credit = sum(float(l["credit_amount"] or 0.0) for l in lines)

        return {
            "voucher": voucher,
            "lines": lines,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "is_balanced": abs(total_debit - total_credit) < 0.01,
            "print_date": datetime.now().strftime("%B %d, %Y %I:%M %p")
        }
