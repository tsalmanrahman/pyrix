from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

MASTER_FUNCTIONS_CATALOG: List[Dict[str, Any]] = [
    # 1. Accounts Payable (AP)
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_VENDOR_MASTER",
        "function_name": "Vendor Profile & Master Accounts",
        "menu_path": "Accounts Payable > Vendors & Profiles",
        "description": "Manage vendor directory, payment terms, tax IDs, and bank details"
    },
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_BILL_ENTRY",
        "function_name": "Purchase Invoices / Bills Entry",
        "menu_path": "Accounts Payable > Bills & Invoices",
        "description": "Create, review, and post supplier bills and purchase invoices"
    },
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_DEBIT_NOTE",
        "function_name": "Debit Notes & Vendor Returns",
        "menu_path": "Accounts Payable > Debit Notes",
        "description": "Issue debit memos and purchase return adjustments"
    },
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_PAYMENT_VOUCHER",
        "function_name": "Vendor Payment Disbursals",
        "menu_path": "Accounts Payable > Outgoing Payments",
        "description": "Prepare, approve, and disburse cheque / electronic vendor payments"
    },
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_EXPENSE_CLAIM",
        "function_name": "Staff Expense Claims & Settlements",
        "menu_path": "Accounts Payable > Expense Claims",
        "description": "Process employee out-of-pocket claims and settlements"
    },
    {
        "module_code": "AP",
        "module_name": "Accounts Payable",
        "function_code": "AP_AGING_REPORTS",
        "function_name": "Vendor Aging & Payable Registers",
        "menu_path": "Accounts Payable > Reports & Inquiries",
        "description": "View and export vendor aging analysis and invoice ledgers"
    },

    # 2. General Ledger (GL)
    {
        "module_code": "GL",
        "module_name": "General Ledger",
        "function_code": "GL_COA_MASTER",
        "function_name": "Chart of Accounts Structure",
        "menu_path": "General Ledger > Chart of Accounts",
        "description": "Maintain master accounts, account heads, groupings, and currency links"
    },
    {
        "module_code": "GL",
        "module_name": "General Ledger",
        "function_code": "GL_JOURNAL_VOUCHER",
        "function_name": "Manual & Recurring Journal Entries",
        "menu_path": "General Ledger > General Journals",
        "description": "Post debit/credit journal vouchers, adjustments, and accruals"
    },
    {
        "module_code": "GL",
        "module_name": "General Ledger",
        "function_code": "GL_BUDGETING",
        "function_name": "Departmental Annual Budgets",
        "menu_path": "General Ledger > Budgets & Forecasts",
        "description": "Configure financial year budget limits and variance controls"
    },
    {
        "module_code": "GL",
        "module_name": "General Ledger",
        "function_code": "GL_PERIODIC_CLOSE",
        "function_name": "Period End Locks & Closing",
        "menu_path": "General Ledger > Periodic Processing",
        "description": "Lock monthly accounting periods and execute year-end balance rolls"
    },
    {
        "module_code": "GL",
        "module_name": "General Ledger",
        "function_code": "GL_FINANCIAL_STMTS",
        "function_name": "Financial Statements & Trial Balance",
        "menu_path": "General Ledger > Statements & Reports",
        "description": "Generate Balance Sheet, Profit & Loss, Cash Flow, and Trial Balance"
    },

    # 3. Accounts Receivable (AR)
    {
        "module_code": "AR",
        "module_name": "Accounts Receivable",
        "function_code": "AR_CUSTOMER_MASTER",
        "function_name": "Customer Accounts & Credit Limits",
        "menu_path": "Accounts Receivable > Customers",
        "description": "Customer profiles, credit limit approvals, and contact directories"
    },
    {
        "module_code": "AR",
        "module_name": "Accounts Receivable",
        "function_code": "AR_SALES_INVOICE",
        "function_name": "Direct Sales Billing & Tax Invoices",
        "menu_path": "Accounts Receivable > Sales Invoices",
        "description": "Issue customer commercial and statutory tax invoices"
    },
    {
        "module_code": "AR",
        "module_name": "Accounts Receivable",
        "function_code": "AR_CREDIT_NOTE",
        "function_name": "Credit Notes & Sales Returns",
        "menu_path": "Accounts Receivable > Credit Notes",
        "description": "Approve credit memos, price concessions, and customer refunds"
    },
    {
        "module_code": "AR",
        "module_name": "Accounts Receivable",
        "function_code": "AR_RECEIPT_VOUCHER",
        "function_name": "Customer Collection Receipts",
        "menu_path": "Accounts Receivable > Incoming Receipts",
        "description": "Post payment collections, bank deposits, and invoice knock-offs"
    },
    {
        "module_code": "AR",
        "module_name": "Accounts Receivable",
        "function_code": "AR_AGING_REPORTS",
        "function_name": "AR Outstanding Aging & Statements",
        "menu_path": "Accounts Receivable > Statements & Aging",
        "description": "Review receivable aging schedules and customer statement runs"
    },

    # 4. Sales & Distribution (SLS)
    {
        "module_code": "SLS",
        "module_name": "Sales & Distribution",
        "function_code": "SLS_PRICE_LIST",
        "function_name": "Price Books & Customer Discount Tiers",
        "menu_path": "Sales > Pricing & Contracts",
        "description": "Manage base rates, promotional schemes, and customer-specific tariffs"
    },
    {
        "module_code": "SLS",
        "module_name": "Sales & Distribution",
        "function_code": "SLS_SALES_ORDER",
        "function_name": "Sales Orders & Quotations",
        "menu_path": "Sales > Orders & Quotations",
        "description": "Book client orders, quotations, and contract commitments"
    },
    {
        "module_code": "SLS",
        "module_name": "Sales & Distribution",
        "function_code": "SLS_DISPATCH_NOTE",
        "function_name": "Delivery Notes & Logistics Waybills",
        "menu_path": "Sales > Dispatch & Shipping",
        "description": "Generate packing slips, dispatch notes, and carrier waybills"
    },
    {
        "module_code": "SLS",
        "module_name": "Sales & Distribution",
        "function_code": "SLS_COMMISSION",
        "function_name": "Sales Representative Commissions",
        "menu_path": "Sales > Performance & Commissions",
        "description": "Calculate and approve sales commission payouts and bonus targets"
    },

    # 5. Inventory & Warehousing (INV)
    {
        "module_code": "INV",
        "module_name": "Inventory & Warehousing",
        "function_code": "INV_ITEM_MASTER",
        "function_name": "Stock Items, SKUs & Barcodes",
        "menu_path": "Inventory > Item Master",
        "description": "Maintain SKU catalog, UOM conversions, reorder levels, and pricing"
    },
    {
        "module_code": "INV",
        "module_name": "Inventory & Warehousing",
        "function_code": "INV_GOODS_RECEIPT",
        "function_name": "Goods Receipt Notes (GRN)",
        "menu_path": "Inventory > Receipts & Inbound",
        "description": "Record inbound shipments, inspection reports, and warehouse binning"
    },
    {
        "module_code": "INV",
        "module_name": "Inventory & Warehousing",
        "function_code": "INV_STOCK_TRANSFER",
        "function_name": "Inter-Warehouse Stock Transfers",
        "menu_path": "Inventory > Transfers",
        "description": "Authorise stock movements between plants, stores, and transit nodes"
    },
    {
        "module_code": "INV",
        "module_name": "Inventory & Warehousing",
        "function_code": "INV_STOCK_ADJUST",
        "function_name": "Physical Inventory & Stock Adjustments",
        "menu_path": "Inventory > Stock Adjustments",
        "description": "Post cycle count variances, write-offs, and batch reclassifications"
    },
    {
        "module_code": "INV",
        "module_name": "Inventory & Warehousing",
        "function_code": "INV_VALUATION",
        "function_name": "Inventory Valuation & Movement Ledger",
        "menu_path": "Inventory > Valuation & Ledger",
        "description": "Moving average / FIFO cost tracking, stock card, and inventory audits"
    },

    # 6. Production & Manufacturing (PROD)
    {
        "module_code": "PROD",
        "module_name": "Production & Manufacturing",
        "function_code": "PROD_BOM_MASTER",
        "function_name": "Bills of Materials (BOM) & Routings",
        "menu_path": "Manufacturing > Engineering & BOM",
        "description": "Engineering BOM recipes, assembly stages, and machine work centers"
    },
    {
        "module_code": "PROD",
        "module_name": "Production & Manufacturing",
        "function_code": "PROD_WORK_ORDER",
        "function_name": "Production Work Orders",
        "menu_path": "Manufacturing > Work Orders",
        "description": "Schedule production runs, issue raw materials, and backflush components"
    },
    {
        "module_code": "PROD",
        "module_name": "Production & Manufacturing",
        "function_code": "PROD_JOB_CARD",
        "function_name": "Shopfloor Job Cards & Workstations",
        "menu_path": "Manufacturing > Shopfloor Execution",
        "description": "Track operator labor, workstation machine hours, and downtime"
    },
    {
        "module_code": "PROD",
        "module_name": "Production & Manufacturing",
        "function_code": "PROD_QC_INSPECTION",
        "function_name": "Quality Assurance & Batch Release",
        "menu_path": "Manufacturing > Quality Control",
        "description": "QA sampling parameters, Certificate of Analysis (CoA), and quarantine"
    },

    # 7. Fixed Assets (FA)
    {
        "module_code": "FA",
        "module_name": "Fixed Assets",
        "function_code": "FA_ASSET_REGISTER",
        "function_name": "Asset Capitalization & Register",
        "menu_path": "Fixed Assets > Asset Register",
        "description": "Tagging equipment, capitalization costs, locations, and custodians"
    },
    {
        "module_code": "FA",
        "module_name": "Fixed Assets",
        "function_code": "FA_DEPRECIATION",
        "function_name": "Periodic Depreciation Execution",
        "menu_path": "Fixed Assets > Depreciation Processing",
        "description": "Calculate and post straight-line or reducing balance depreciation"
    },
    {
        "module_code": "FA",
        "module_name": "Fixed Assets",
        "function_code": "FA_DISPOSAL",
        "function_name": "Asset Disposals, Scrap & Transfers",
        "menu_path": "Fixed Assets > Disposals & Revaluation",
        "description": "Process asset retirement, write-downs, auction sales, and profit/loss"
    },

    # 8. Human Resources & Payroll (HR)
    {
        "module_code": "HR",
        "module_name": "Human Resources & Payroll",
        "function_code": "HR_EMPLOYEE_MASTER",
        "function_name": "Personnel Files & Contracts",
        "menu_path": "Human Resources > Employee Directory",
        "description": "Staff profile, employment contracts, salary structures, and compliance"
    },
    {
        "module_code": "HR",
        "module_name": "Human Resources & Payroll",
        "function_code": "HR_ATTENDANCE",
        "function_name": "Attendance, Leaves & Shift Rosters",
        "menu_path": "Human Resources > Attendance & Leaves",
        "description": "Biometric logs, leave approvals, shifts, and overtime calculations"
    },
    {
        "module_code": "HR",
        "module_name": "Human Resources & Payroll",
        "function_code": "HR_PAYROLL_RUN",
        "function_name": "Monthly Payroll Processing",
        "menu_path": "Human Resources > Payroll Processing",
        "description": "Execute monthly payroll calculations, tax deductions, and bank advices"
    },

    # 9. Cash & Banking (CB)
    {
        "module_code": "CB",
        "module_name": "Cash & Banking",
        "function_code": "CB_BANK_ACCOUNTS",
        "function_name": "Bank Accounts & Cheque Registers",
        "menu_path": "Cash & Banking > Accounts & Mandates",
        "description": "Bank account profiles, signatories, cheque leaf inventory, and IBANs"
    },
    {
        "module_code": "CB",
        "module_name": "Cash & Banking",
        "function_code": "CB_CASH_VOUCHERS",
        "function_name": "Petty Cash Books & Floats",
        "menu_path": "Cash & Banking > Petty Cash",
        "description": "Petty cash vouchers, branch float top-ups, and petty reconciliations"
    },
    {
        "module_code": "CB",
        "module_name": "Cash & Banking",
        "function_code": "CB_BANK_RECON",
        "function_name": "Bank Statement Reconciliation (BRS)",
        "menu_path": "Cash & Banking > Reconciliation",
        "description": "Match bank statement feeds against book records and clear unpresented cheques"
    },
    {
        "module_code": "CB",
        "module_name": "Cash & Banking",
        "function_code": "CB_FUND_TRANSFER",
        "function_name": "Inter-Account Fund Transfers",
        "menu_path": "Cash & Banking > Fund Transfers",
        "description": "Authorise treasury transfers between corporate bank and cash accounts"
    },

    # 10. System Administration & Security (ADM)
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_USER_PROFILES",
        "function_name": "Enterprise User Accounts & Access",
        "menu_path": "System Admin > User Profiles",
        "description": "Create users, reset credentials, assign clearance tiers, and lockouts"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_USER_AUTHORIZATION",
        "function_name": "User Authorization & Granular Permissions",
        "menu_path": "System Admin > User Authorisation",
        "description": "Assign user-specific Create, Edit, Delete, View, Approve, and Export rights"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_ROLE_MATRIX",
        "function_name": "Role-Based Access Control (RBAC)",
        "menu_path": "System Admin > Roles & RBAC",
        "description": "Configure organizational security roles and default permission blueprints"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_COMPANY_SETUP",
        "function_name": "Multi-Company & Subsidiary Profiles",
        "menu_path": "System Admin > Company Profiles",
        "description": "Corporate entities, legal registrations, fiscal calendars, and currencies"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_TAX_CONFIG",
        "function_name": "Statutory Tax Regimes & Slabs",
        "menu_path": "System Admin > Tax Configuration",
        "description": "Configure VAT rates, withholding slabs, and tax authority profiles"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_PERIOD_CLOSING",
        "function_name": "Fiscal Period Closures & Year-End",
        "menu_path": "System Admin > Maintenance & Closures",
        "description": "Administer period freeze locks, financial year closure, and balance roll"
    },
    {
        "module_code": "ADM",
        "module_name": "System Administration",
        "function_code": "ADM_AUDIT_LOG",
        "function_name": "Tamper-Evident Security Audit Vault",
        "menu_path": "System Admin > Audit Vault",
        "description": "Review immutable audit trails, IP logs, mutation history, and compliance scans"
    }
]


class PermissionService:
    @staticmethod
    def ensure_schema():
        """Ensures that the admin_user_permissions table and allow_closed_years column exist."""
        try:
            db.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_user_permissions')
                BEGIN
                    CREATE TABLE admin_user_permissions (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        user_id VARCHAR(64) NOT NULL,
                        company_id VARCHAR(64) NOT NULL DEFAULT 'ALL',
                        module_code VARCHAR(30) NOT NULL,
                        function_code VARCHAR(100) NOT NULL,
                        function_name NVARCHAR(200) NOT NULL,
                        menu_path NVARCHAR(200) NOT NULL,
                        can_view BIT DEFAULT 0,
                        can_create BIT DEFAULT 0,
                        can_edit BIT DEFAULT 0,
                        can_delete BIT DEFAULT 0,
                        can_approve BIT DEFAULT 0,
                        can_export BIT DEFAULT 0,
                        allow_closed_years BIT DEFAULT 0,
                        updated_by VARCHAR(64) NULL,
                        updated_at DATETIME DEFAULT GETDATE(),
                        CONSTRAINT UQ_admin_user_perms UNIQUE (user_id, company_id, function_code)
                    );
                    CREATE INDEX IX_user_perms_lookup ON admin_user_permissions(user_id, company_id);
                END
            """)
        except Exception as e:
            print(f"[PermissionService] Notice on ensure table: {e}")

        try:
            db.execute("""
                IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'allow_closed_years')
                BEGIN
                    ALTER TABLE users ADD allow_closed_years BIT DEFAULT 0;
                END
            """)
        except Exception as e:
            print(f"[PermissionService] Notice on ensure users column: {e}")

    @staticmethod
    def get_catalog() -> List[Dict[str, Any]]:
        """Returns the master list of all 10 ERP modules and granular functions."""
        return MASTER_FUNCTIONS_CATALOG

    @staticmethod
    def get_user_permissions(user_id: str, company_id: str = "ALL") -> Dict[str, Any]:
        """
        Retrieves user permission rows for the specified user and company.
        Merges existing database records with the Master Functions Catalog.
        Returns a dict containing:
          - user_id
          - company_id
          - allow_closed_years (bool)
          - permissions: list of all functions with resolved boolean flags
        """
        PermissionService.ensure_schema()
        safe_cid = company_id.strip() if company_id and company_id.strip() else "ALL"

        # Check user's allow_closed_years flag
        user_row = db.query_one("SELECT allow_closed_years FROM users WHERE id = ?", (user_id,))
        allow_closed_years = bool(user_row.get("allow_closed_years", 0)) if user_row else False

        # Query explicit permissions for this user + company
        rows = db.query(
            """
            SELECT * FROM admin_user_permissions
            WHERE user_id = ? AND company_id = ?
            """,
            (user_id, safe_cid)
        )

        perm_map = {r["function_code"]: r for r in rows}

        merged_list = []
        for cat in MASTER_FUNCTIONS_CATALOG:
            fcode = cat["function_code"]
            existing = perm_map.get(fcode)
            if existing:
                merged_list.append({
                    "module_code": cat["module_code"],
                    "module_name": cat["module_name"],
                    "function_code": fcode,
                    "function_name": cat["function_name"],
                    "menu_path": cat["menu_path"],
                    "description": cat.get("description", ""),
                    "can_view": bool(existing.get("can_view", 0)),
                    "can_create": bool(existing.get("can_create", 0)),
                    "can_edit": bool(existing.get("can_edit", 0)),
                    "can_delete": bool(existing.get("can_delete", 0)),
                    "can_approve": bool(existing.get("can_approve", 0)),
                    "can_export": bool(existing.get("can_export", 0)),
                    "allow_closed_years": bool(existing.get("allow_closed_years", 0)),
                })
            else:
                # Default permissions based on user clearance or role
                merged_list.append({
                    "module_code": cat["module_code"],
                    "module_name": cat["module_name"],
                    "function_code": fcode,
                    "function_name": cat["function_name"],
                    "menu_path": cat["menu_path"],
                    "description": cat.get("description", ""),
                    "can_view": False,
                    "can_create": False,
                    "can_edit": False,
                    "can_delete": False,
                    "can_approve": False,
                    "can_export": False,
                    "allow_closed_years": False,
                })

        return {
            "user_id": user_id,
            "company_id": safe_cid,
            "allow_closed_years": allow_closed_years,
            "permissions": merged_list
        }

    @staticmethod
    def save_user_permissions(
        user_id: str,
        company_id: str,
        allow_closed_years: bool,
        permissions_list: List[Dict[str, Any]],
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Persists full permission matrix for a user in atomic batches.
        Updates user-level 'allow_closed_years' and UPSERTs each function record.
        """
        PermissionService.ensure_schema()
        safe_cid = company_id.strip() if company_id and company_id.strip() else "ALL"

        # 1. Update user allow_closed_years
        try:
            db.execute(
                "UPDATE users SET allow_closed_years = ? WHERE id = ?",
                (1 if allow_closed_years else 0, user_id)
            )
        except Exception as e:
            print(f"[PermissionService] Error updating users allow_closed_years: {e}")

        # 2. Upsert each permission record
        for p in permissions_list:
            fcode = p.get("function_code")
            if not fcode:
                continue
            
            # Find catalog details
            cat = next((c for c in MASTER_FUNCTIONS_CATALOG if c["function_code"] == fcode), None)
            mcode = cat["module_code"] if cat else p.get("module_code", "GEN")
            fname = cat["function_name"] if cat else p.get("function_name", fcode)
            mpath = cat["menu_path"] if cat else p.get("menu_path", "")

            can_view = 1 if p.get("can_view") else 0
            can_create = 1 if p.get("can_create") else 0
            can_edit = 1 if p.get("can_edit") else 0
            can_delete = 1 if p.get("can_delete") else 0
            can_approve = 1 if p.get("can_approve") else 0
            can_export = 1 if p.get("can_export") else 0

            # Use MS SQL MERGE for clean atomic UPSERT
            upsert_sql = """
                MERGE INTO admin_user_permissions AS target
                USING (SELECT ? AS user_id, ? AS company_id, ? AS function_code) AS source
                ON (target.user_id = source.user_id AND target.company_id = source.company_id AND target.function_code = source.function_code)
                WHEN MATCHED THEN
                    UPDATE SET
                        module_code = ?,
                        function_name = ?,
                        menu_path = ?,
                        can_view = ?,
                        can_create = ?,
                        can_edit = ?,
                        can_delete = ?,
                        can_approve = ?,
                        can_export = ?,
                        allow_closed_years = ?,
                        updated_by = ?,
                        updated_at = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (
                        user_id, company_id, module_code, function_code, function_name, menu_path,
                        can_view, can_create, can_edit, can_delete, can_approve, can_export,
                        allow_closed_years, updated_by, updated_at
                    )
                    VALUES (
                        source.user_id, source.company_id, ?, source.function_code, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, GETDATE()
                    );
            """
            params = (
                user_id, safe_cid, fcode,
                # UPDATE params:
                mcode, fname, mpath, can_view, can_create, can_edit, can_delete, can_approve, can_export,
                1 if allow_closed_years else 0, updated_by,
                # INSERT params:
                mcode, fname, mpath, can_view, can_create, can_edit, can_delete, can_approve, can_export,
                1 if allow_closed_years else 0, updated_by
            )
            db.execute(upsert_sql, params)

        return True

    @staticmethod
    def check_user_permission(
        user_id: str,
        function_code: str,
        action: str = "view",
        company_id: Optional[str] = None
    ) -> bool:
        """
        Fast security authorization check:
        action can be 'view', 'create', 'edit', 'delete', 'approve', 'export'.
        Checks user-specific permission, falling back to company 'ALL'.
        Super Admins (clearance TIER_4_ROOT or TIER_3_GROUP) bypass and return True.
        """
        # Check if user is Super Admin
        user = db.query_one("SELECT clearance_tier FROM users WHERE id = ?", (user_id,))
        if user and user.get("clearance_tier") in ("TIER_4_ROOT", "TIER_3_GROUP"):
            return True

        action_col_map = {
            "view": "can_view",
            "create": "can_create",
            "edit": "can_edit",
            "modify": "can_edit",
            "delete": "can_delete",
            "approve": "can_approve",
            "export": "can_export",
        }
        col = action_col_map.get(action.lower(), "can_view")

        # First check specific company
        if company_id and company_id != "ALL":
            row = db.query_one(
                f"SELECT {col} FROM admin_user_permissions WHERE user_id = ? AND company_id = ? AND function_code = ?",
                (user_id, company_id, function_code)
            )
            if row is not None:
                return bool(row.get(col, 0))

        # Check conglomerate-wide (company_id = 'ALL')
        row_all = db.query_one(
            f"SELECT {col} FROM admin_user_permissions WHERE user_id = ? AND company_id = 'ALL' AND function_code = ?",
            (user_id, function_code)
        )
        if row_all is not None:
            return bool(row_all.get(col, 0))

        return False
