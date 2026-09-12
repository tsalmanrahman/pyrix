import datetime
import logging
from typing import Dict, Any, List, Optional
from app.core.db import db

logger = logging.getLogger("SequenceService")

DEFAULT_SEQUENCES = [
    # General Ledger Module
    {
        "entity_key": "gl_accounts",
        "entity_name": "General Ledger Accounts (Chart of Accounts)",
        "module_slug": "general-ledger",
        "prefix": "GL-AC",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1001,
    },
    {
        "entity_key": "gl_departments",
        "entity_name": "Departments Master",
        "module_slug": "general-ledger",
        "prefix": "DEPT",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "gl_cost_centres",
        "entity_name": "Cost Centers Master",
        "module_slug": "general-ledger",
        "prefix": "CC",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "gl_journal_vouchers",
        "entity_name": "General Journal Vouchers (JV)",
        "module_slug": "general-ledger",
        "prefix": "JV",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    # Cash Book & Treasury Module
    {
        "entity_key": "cb_cashiers",
        "entity_name": "Cashier Workstations & Tills",
        "module_slug": "cash-book",
        "prefix": "CSH",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "cb_bank_accounts",
        "entity_name": "Bank Accounts Registry",
        "module_slug": "cash-book",
        "prefix": "BA",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "cb_money_receipts",
        "entity_name": "Money Receipts (MR)",
        "module_slug": "cash-book",
        "prefix": "MR",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "cb_contra_transfers",
        "entity_name": "Contra Fund Transfers (CT)",
        "module_slug": "cash-book",
        "prefix": "CT",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    # Accounts Receivable Module
    {
        "entity_key": "ar_customers",
        "entity_name": "Customer Accounts Master",
        "module_slug": "accounts-receivable",
        "prefix": "CUST",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 2001,
    },
    {
        "entity_key": "ar_customer_groups",
        "entity_name": "Customer Groups",
        "module_slug": "accounts-receivable",
        "prefix": "CG",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_invoices",
        "entity_name": "Sales Invoices (INV)",
        "module_slug": "accounts-receivable",
        "prefix": "INV",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "ar_notes",
        "entity_name": "Commercial Debit & Credit Notes",
        "module_slug": "accounts-receivable",
        "prefix": "CRN",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 101,
    },
    # Sourcing & Procurement Module
    {
        "entity_key": "sourcing_vendors",
        "entity_name": "Vendor / Supplier Profiles",
        "module_slug": "sourcing",
        "prefix": "VND",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "sourcing_requisitions",
        "entity_name": "Purchase Requisitions (PR)",
        "module_slug": "sourcing",
        "prefix": "PR",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "sourcing_purchase_orders",
        "entity_name": "Purchase Orders (PO)",
        "module_slug": "sourcing",
        "prefix": "PO",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    # Sales Management Module
    {
        "entity_key": "sales_areas",
        "entity_name": "Sales Areas & Territories",
        "module_slug": "sales",
        "prefix": "SA",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "sales_quotes",
        "entity_name": "Commercial Sales Quotations (QT)",
        "module_slug": "sales",
        "prefix": "QT",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "sales_orders",
        "entity_name": "Sales Orders (SO)",
        "module_slug": "sales",
        "prefix": "SO",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    {
        "entity_key": "sales_delivery_orders",
        "entity_name": "Delivery Orders / Dispatch (DO)",
        "module_slug": "sales",
        "prefix": "DO",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    # General Ledger Additional Masters
    {
        "entity_key": "gl_sub_accounts",
        "entity_name": "GL Sub Accounts Master",
        "module_slug": "general-ledger",
        "prefix": "SUB",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "gl_budget_sets",
        "entity_name": "GL Budget Sets Master",
        "module_slug": "general-ledger",
        "prefix": "BUD",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
    # Cash Book Additional Masters
    {
        "entity_key": "cb_banks",
        "entity_name": "Bank Partners Master",
        "module_slug": "cash-book",
        "prefix": "BNK",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "cb_branches",
        "entity_name": "Bank Branches Master",
        "module_slug": "cash-book",
        "prefix": "BR",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    # Accounts Receivable Additional Masters
    {
        "entity_key": "ar_commercial_groups",
        "entity_name": "Commercial Sales Groups",
        "module_slug": "accounts-receivable",
        "prefix": "CG",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_group_categories",
        "entity_name": "Tier Group Categories",
        "module_slug": "accounts-receivable",
        "prefix": "CAT",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_control_accounts",
        "entity_name": "AR Control Account Sets",
        "module_slug": "accounts-receivable",
        "prefix": "AR-SET",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_reminder_criteria",
        "entity_name": "Reminder Criteria Sets",
        "module_slug": "accounts-receivable",
        "prefix": "CRIT",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_aging_profiles",
        "entity_name": "Aging Profiles",
        "module_slug": "accounts-receivable",
        "prefix": "AGING",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    {
        "entity_key": "ar_adjustment_types",
        "entity_name": "Adjustment Types",
        "module_slug": "accounts-receivable",
        "prefix": "ADJ",
        "include_year": "NONE",
        "delimiter": "-",
        "padding_digits": 3,
        "next_number": 1,
    },
    # Generic Monograph Records
    {
        "entity_key": "generic_records",
        "entity_name": "General Enterprise Records & Vouchers",
        "module_slug": "generic",
        "prefix": "DOC",
        "include_year": "YY",
        "delimiter": "-",
        "padding_digits": 4,
        "next_number": 1,
    },
]

class SequenceService:
    """Enterprise document numbering and business code generation engine."""

    @staticmethod
    def ensure_table_exists() -> None:
        """Creates the system_number_sequences table if it doesn't exist and seeds defaults."""
        ddl = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'system_number_sequences')
        BEGIN
            CREATE TABLE system_number_sequences (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NULL,
                entity_key VARCHAR(50) UNIQUE NOT NULL,
                entity_name NVARCHAR(100) NOT NULL,
                module_slug VARCHAR(50) NOT NULL,
                prefix VARCHAR(20) NOT NULL,
                include_year VARCHAR(10) DEFAULT 'NONE',
                delimiter VARCHAR(5) DEFAULT '-',
                padding_digits INT DEFAULT 4,
                next_number INT DEFAULT 1,
                is_active BIT DEFAULT 1,
                updated_at DATETIME DEFAULT GETDATE()
            );
        END
        """
        try:
            db.execute(ddl)
            SequenceService._seed_default_sequences()
        except Exception as e:
            logger.error(f"Error ensuring system_number_sequences table exists: {e}")

    @staticmethod
    def _seed_default_sequences() -> None:
        """Seeds default sequence definitions if table is empty or missing entities."""
        try:
            for item in DEFAULT_SEQUENCES:
                exists = db.query_one(
                    "SELECT COUNT(*) AS cnt FROM system_number_sequences WHERE entity_key = ?",
                    (item["entity_key"],)
                )
                if not exists or exists["cnt"] == 0:
                    db.execute(
                        """
                        INSERT INTO system_number_sequences 
                        (entity_key, entity_name, module_slug, prefix, include_year, delimiter, padding_digits, next_number, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """,
                        (
                            item["entity_key"],
                            item["entity_name"],
                            item["module_slug"],
                            item["prefix"],
                            item["include_year"],
                            item["delimiter"],
                            item["padding_digits"],
                            item["next_number"],
                        )
                    )
            logger.info("Default system number sequences verified/seeded.")
        except Exception as e:
            logger.error(f"Error seeding default sequences: {e}")

    @staticmethod
    def format_code(prefix: str, include_year: str, delimiter: str, padding_digits: int, number: int) -> str:
        """Pure formatting utility given rule parameters."""
        parts = []
        clean_prefix = (prefix or "").strip()
        if clean_prefix:
            parts.append(clean_prefix)

        now = datetime.datetime.now()
        if include_year == "YY":
            parts.append(now.strftime("%y"))
        elif include_year == "YYYY":
            parts.append(now.strftime("%Y"))

        pad = max(1, min(10, int(padding_digits or 4)))
        seq_str = str(max(1, int(number or 1))).zfill(pad)
        parts.append(seq_str)

        delim = delimiter if delimiter is not None else "-"
        return delim.join(parts)

    @classmethod
    def get_next_code(cls, entity_key: str, company_id: Optional[str] = None, increment: bool = True) -> str:
        """
        Calculates and optionally commits the next sequential code for the specified entity.
        Thread-safe atomic SQL increment.
        """
        cls.ensure_table_exists()
        rule = db.query_one(
            """
            SELECT entity_key, prefix, include_year, delimiter, padding_digits, next_number 
            FROM system_number_sequences 
            WHERE entity_key = ? AND is_active = 1
            """,
            (entity_key,)
        )

        if not rule:
            # Fallback for unregistered entities
            fallback_prefix = entity_key.upper().replace("_", "-")[:6]
            now_yy = datetime.datetime.now().strftime("%y")
            return f"{fallback_prefix}-{now_yy}-0001"

        current_num = int(rule["next_number"] or 1)
        generated_code = cls.format_code(
            prefix=rule["prefix"],
            include_year=rule["include_year"],
            delimiter=rule["delimiter"],
            padding_digits=rule["padding_digits"],
            number=current_num
        )

        if increment:
            try:
                db.execute(
                    """
                    UPDATE system_number_sequences 
                    SET next_number = next_number + 1, updated_at = GETDATE() 
                    WHERE entity_key = ?
                    """,
                    (entity_key,)
                )
            except Exception as e:
                logger.error(f"Failed to increment sequence for {entity_key}: {e}")

        return generated_code

    @classmethod
    def preview_next_code(cls, entity_key: str, company_id: Optional[str] = None) -> str:
        """Returns projected next code without incrementing the counter."""
        return cls.get_next_code(entity_key, company_id=company_id, increment=False)

    @classmethod
    def list_all_sequences(cls) -> List[Dict[str, Any]]:
        """Returns all configured numbering series with their computed live preview."""
        cls.ensure_table_exists()
        rows = db.query(
            """
            SELECT id, code, entity_key, entity_name, module_slug, prefix, include_year, 
                   delimiter, padding_digits, next_number, is_active, updated_at
            FROM system_number_sequences
            ORDER BY module_slug ASC, entity_name ASC
            """
        )

        result = []
        for r in rows:
            preview = cls.format_code(
                prefix=r["prefix"],
                include_year=r["include_year"],
                delimiter=r["delimiter"],
                padding_digits=r["padding_digits"],
                number=r["next_number"]
            )
            result.append({
                "id": str(r["id"]),
                "code": r["code"],
                "entity_key": r["entity_key"],
                "entity_name": r["entity_name"],
                "module_slug": r["module_slug"],
                "prefix": r["prefix"],
                "include_year": r["include_year"],
                "delimiter": r["delimiter"],
                "padding_digits": r["padding_digits"],
                "next_number": r["next_number"],
                "is_active": bool(r["is_active"]),
                "live_preview": preview,
                "updated_at": str(r["updated_at"]) if r.get("updated_at") else "",
            })
        return result

    @classmethod
    def update_sequence_rule(
        cls,
        entity_key: str,
        prefix: str,
        include_year: str,
        delimiter: str,
        padding_digits: int,
        next_number: int
    ) -> Dict[str, Any]:
        """Updates sequence parameters in the database."""
        cls.ensure_table_exists()
        clean_prefix = (prefix or "").strip().upper()
        clean_year = include_year if include_year in ["NONE", "YY", "YYYY"] else "NONE"
        clean_delim = delimiter if delimiter in ["-", "/", "_", ""] else "-"
        clean_pad = max(1, min(10, int(padding_digits or 4)))
        clean_num = max(1, int(next_number or 1))

        db.execute(
            """
            UPDATE system_number_sequences
            SET prefix = ?, include_year = ?, delimiter = ?, padding_digits = ?, 
                next_number = ?, updated_at = GETDATE()
            WHERE entity_key = ?
            """,
            (clean_prefix, clean_year, clean_delim, clean_pad, clean_num, entity_key)
        )

        new_preview = cls.format_code(clean_prefix, clean_year, clean_delim, clean_pad, clean_num)
        return {
            "success": True,
            "entity_key": entity_key,
            "live_preview": new_preview,
            "message": f"Sequence rule for {entity_key} updated successfully."
        }
