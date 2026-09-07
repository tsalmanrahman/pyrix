"""
Data Migration & Sequence Counter Synchronization Utility
=========================================================
Standardizes all legacy and arbitrary business code data across PyrixDB
master and transactional tables to strictly adhere to administrator-defined
numbering sequence rules in system_number_sequences.

Preserves full audit trail and rollback safety via _backup_code_data_migration.
"""

import sys
import logging
from typing import Dict, Any, List, Tuple
from app.core.db import db
from app.core.sequence_service import SequenceService

logger = logging.getLogger("CodeMigration")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Complete table and column mapping for all 29 sequence definitions
SEQUENCE_TABLE_MAP: Dict[str, Tuple[str, str]] = {
    # General Ledger Module
    "gl_accounts": ("gl_accounts", "account_number"),
    "gl_sub_accounts": ("gl_sub_accounts", "sub_account_code"),
    "gl_departments": ("gl_departments", "dept_code"),
    "gl_cost_centres": ("gl_cost_centres", "cost_centre_code"),
    "gl_budget_sets": ("gl_budget_sets", "budget_code"),
    "gl_journal_vouchers": ("gl_journal_vouchers", "voucher_number"),

    # Cash Book & Treasury Module
    "cb_cashiers": ("cb_cashiers", "cashier_code"),
    "cb_banks": ("cb_banks", "bank_code"),
    "cb_branches": ("cb_bank_branches", "branch_code"),
    "cb_bank_accounts": ("cb_bank_accounts", "account_number"),
    "cb_money_receipts": ("cb_money_receipts", "receipt_number"),
    "cb_contra_transfers": ("cb_contra_transfers", "transfer_number"),

    # Accounts Receivable Module
    "ar_customers": ("ar_customers", "customer_code"),
    "ar_customer_groups": ("ar_customer_groups", "group_code"),
    "ar_group_categories": ("ar_group_categories", "category_code"),
    "ar_commercial_groups": ("ar_commercial_groups", "group_code"),
    "ar_control_accounts": ("ar_control_account_sets", "set_code"),
    "ar_reminder_criteria": ("ar_reminder_criteria", "criteria_code"),
    "ar_aging_profiles": ("ar_aging_profiles", "profile_code"),
    "ar_adjustment_types": ("ar_adjustment_types", "adjustment_code"),
    "ar_invoices": ("sales_invoices", "invoice_number"),

    # Sourcing & Procurement Module
    "sourcing_vendors": ("sourcing_vendors", "vendor_code"),
    "sourcing_requisitions": ("sourcing_requisitions", "req_number"),
    "sourcing_purchase_orders": ("sourcing_purchase_orders", "po_number"),

    # Sales Management Module
    "sales_areas": ("sales_areas", "area_code"),
    "sales_quotes": ("sales_quotes", "quote_number"),
    "sales_orders": ("sales_orders", "order_number"),
    "sales_delivery_orders": ("sales_delivery_orders", "do_number"),

    # Generic Module Records
    "generic_records": ("module_records", "ref_number"),
}


class CodeMigrationService:
    @classmethod
    def ensure_backup_table(cls):
        """Creates audit and safety backup table if not already present."""
        db.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '_backup_code_data_migration')
            BEGIN
                CREATE TABLE _backup_code_data_migration (
                    id UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
                    record_id UNIQUEIDENTIFIER NOT NULL,
                    table_name VARCHAR(100) NOT NULL,
                    column_name VARCHAR(100) NOT NULL,
                    old_code NVARCHAR(255),
                    new_code NVARCHAR(255),
                    entity_key VARCHAR(80) NOT NULL,
                    migrated_at DATETIME DEFAULT GETDATE()
                );
            END
        """)

    @classmethod
    def run_migration(cls, dry_run: bool = False) -> Dict[str, Any]:
        """
        Executes code standardization migration across all mapped tables.
        Synchronizes sequence next_number counters to follow migrated data.
        """
        cls.ensure_backup_table()
        all_sequences = SequenceService.list_all_sequences()
        seq_dict = {s["entity_key"]: s for s in all_sequences}

        migration_summary: List[Dict[str, Any]] = []
        total_records_updated = 0

        for entity_key, (table_name, column_name) in SEQUENCE_TABLE_MAP.items():
            rule = seq_dict.get(entity_key)
            if not rule:
                logger.warning(f"No sequence rule configured for entity: {entity_key}")
                continue

            # Verify table and column in DB
            tbl_check = db.query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (table_name,))
            if not tbl_check:
                logger.error(f"Target table {table_name} does not exist. Skipping.")
                continue

            col_check = db.query(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? AND COLUMN_NAME = ?",
                (table_name, column_name)
            )
            if not col_check:
                logger.error(f"Target column {table_name}.{column_name} does not exist. Skipping.")
                continue

            # Order by surrogate identity code ASC (or id ASC) to preserve chronology
            has_code_col = db.query(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? AND COLUMN_NAME = 'code'",
                (table_name,)
            )
            order_by = "code ASC" if has_code_col else "id ASC"

            records = db.query(f"SELECT id, [{column_name}] as curr_code FROM [{table_name}] ORDER BY {order_by}")
            if not records:
                migration_summary.append({
                    "entity_key": entity_key,
                    "table": table_name,
                    "column": column_name,
                    "count": 0,
                    "status": "SKIPPED_EMPTY",
                    "next_number": rule["next_number"]
                })
                continue

            prefix = rule["prefix"]
            include_year = rule["include_year"]
            delimiter = rule["delimiter"]
            padding = rule["padding_digits"]
            start_num = rule["next_number"]

            current_counter = start_num
            table_updates = []

            for row in records:
                rec_id = str(row["id"])
                old_val = row["curr_code"] or ""
                new_val = SequenceService.format_code(
                    prefix=prefix,
                    include_year=include_year,
                    delimiter=delimiter,
                    padding_digits=padding,
                    number=current_counter
                )

                table_updates.append((rec_id, old_val, new_val))
                current_counter += 1

            if not dry_run:
                # Apply updates atomically per table
                for rec_id, old_val, new_val in table_updates:
                    # 1. Record in backup snapshot table
                    db.execute("""
                        INSERT INTO _backup_code_data_migration 
                        (record_id, table_name, column_name, old_code, new_code, entity_key, migrated_at)
                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                    """, (rec_id, table_name, column_name, old_val, new_val, entity_key))

                    # 2. Update target table column
                    db.execute(
                        f"UPDATE [{table_name}] SET [{column_name}] = ? WHERE id = ?",
                        (new_val, rec_id)
                    )

                # 3. Synchronize next_number counter in system_number_sequences
                db.execute("""
                    UPDATE system_number_sequences 
                    SET next_number = ?, updated_at = GETDATE()
                    WHERE entity_key = ?
                """, (current_counter, entity_key))

            total_records_updated += len(table_updates)
            migration_summary.append({
                "entity_key": entity_key,
                "table": table_name,
                "column": column_name,
                "count": len(table_updates),
                "first_code": table_updates[0][2] if table_updates else None,
                "last_code": table_updates[-1][2] if table_updates else None,
                "next_number_after": current_counter,
                "status": "MIGRATED" if not dry_run else "DRY_RUN_OK"
            })

            logger.info(
                f"[{'DRY-RUN' if dry_run else 'COMMITTED'}] {table_name}.{column_name}: "
                f"{len(table_updates)} records updated. Next sequence: {current_counter}"
            )

        return {
            "success": True,
            "dry_run": dry_run,
            "total_tables_processed": len(migration_summary),
            "total_records_updated": total_records_updated,
            "summary": migration_summary
        }

    @classmethod
    def rollback_migration(cls) -> Dict[str, Any]:
        """
        Reverts records to their previous old_code stored in _backup_code_data_migration.
        """
        cls.ensure_backup_table()
        backups = db.query("""
            SELECT record_id, table_name, column_name, old_code, entity_key 
            FROM _backup_code_data_migration
            ORDER BY migrated_at DESC
        """)

        if not backups:
            return {"success": False, "message": "No migration backup history found to roll back."}

        reverted_count = 0
        for b in backups:
            rec_id = str(b["record_id"])
            tbl = b["table_name"]
            col = b["column_name"]
            old_code = b["old_code"]

            db.execute(
                f"UPDATE [{tbl}] SET [{col}] = ? WHERE id = ?",
                (old_code, rec_id)
            )
            reverted_count += 1

        return {
            "success": True,
            "reverted_records": reverted_count,
            "message": f"Successfully restored {reverted_count} original codes from backup."
        }


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    print(f"\\n{'='*70}")
    print(f"STARTING CODE MIGRATION (Mode: {'DRY RUN' if is_dry else 'LIVE EXECUTION'})")
    print(f"{'='*70}\\n")
    res = CodeMigrationService.run_migration(dry_run=is_dry)
    print(f"\\nMigration completed! Total tables: {res['total_tables_processed']}, Total records: {res['total_records_updated']}")
    print(f"{'='*70}\\n")
