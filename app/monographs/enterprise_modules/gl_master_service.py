from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class GLMasterService:

    # =========================================================================
    # 1. GL Accounts (Chart of Accounts)
    # =========================================================================
    STANDARD_ACCOUNT_GROUPS = [
        "Current Assets",
        "Non-Current Assets / Fixed Assets",
        "Intangibles & Long-term Investments",
        "Current Liabilities",
        "Non-Current / Long-Term Liabilities",
        "Shareholders' Equity / Paid-up Capital",
        "Operating Revenue / Gross Sales",
        "Non-Operating & Investment Income",
        "Cost of Goods Sold (COGS)",
        "Operating Expenses (OPEX)",
        "Administrative & General Expenses",
        "Selling & Distribution Expenses",
        "Financial & Bank Charges",
        "Taxation & Statutory Provisions"
    ]

    @staticmethod
    def get_account_groups() -> List[str]:
        # Return distinct groups from DB merged with standard groups
        db_groups = db.query("SELECT DISTINCT account_group FROM gl_accounts WHERE account_group IS NOT NULL AND COALESCE(isDelete, 0) = 0")
        groups = set(GLMasterService.STANDARD_ACCOUNT_GROUPS)
        for g in db_groups:
            if g.get("account_group"):
                groups.add(g["account_group"])
        return sorted(list(groups))

    @staticmethod
    def is_account_name_unique(account_name: str, exclude_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        sql = "SELECT id, account_number FROM gl_accounts WHERE LOWER(TRIM(account_name)) = LOWER(TRIM(?)) AND COALESCE(isDelete, 0) = 0"
        params = [account_name]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        row = db.query_one(sql, tuple(params))
        if row:
            return False, row.get("account_number")
        return True, None

    @staticmethod
    def get_all_accounts() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM gl_accounts WHERE COALESCE(isDelete, 0) = 0 ORDER BY account_number ASC")

    @staticmethod
    def get_account_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM gl_accounts WHERE id = ? AND COALESCE(isDelete, 0) = 0", (account_id,))

    @staticmethod
    def create_account(
        account_number: str, 
        account_name: str, 
        account_type: str, 
        financial_statement: str, 
        normal_balance: str,
        account_group: Optional[str] = None,
        account_class: str = "POSTING",
        posting_form: str = "DETAILED",
        maintain_quantity: bool = False,
        cost_centre_associated: bool = False,
        is_inactive: bool = False
    ) -> None:
        is_unique, existing_code = GLMasterService.is_account_name_unique(account_name)
        if not is_unique:
            raise ValueError(f"Account name '{account_name.strip()}' already exists (Code: {existing_code}).")

        db.execute(
            """
            INSERT INTO gl_accounts (
                account_number, account_name, account_type, financial_statement, normal_balance, 
                account_group, account_class, posting_form, maintain_quantity, cost_centre_associated, 
                is_inactive, is_active, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                account_number.strip(), account_name.strip(), account_type.strip(), 
                financial_statement.strip(), normal_balance.strip(),
                account_group.strip() if account_group else None,
                account_class.strip() if account_class else "POSTING",
                posting_form.strip() if posting_form else "DETAILED",
                1 if maintain_quantity else 0,
                1 if cost_centre_associated else 0,
                1 if is_inactive else 0,
                0 if is_inactive else 1
            )
        )

    @staticmethod
    def update_account(
        account_id: str, 
        account_number: str, 
        account_name: str, 
        account_type: str, 
        financial_statement: str, 
        normal_balance: str,
        account_group: Optional[str] = None,
        account_class: str = "POSTING",
        posting_form: str = "DETAILED",
        maintain_quantity: bool = False,
        cost_centre_associated: bool = False,
        is_inactive: bool = False
    ) -> None:
        is_unique, existing_code = GLMasterService.is_account_name_unique(account_name, exclude_id=account_id)
        if not is_unique:
            raise ValueError(f"Account name '{account_name.strip()}' already exists (Code: {existing_code}).")

        db.execute(
            """
            UPDATE gl_accounts 
            SET account_number = ?, account_name = ?, account_type = ?, financial_statement = ?, normal_balance = ?,
                account_group = ?, account_class = ?, posting_form = ?, maintain_quantity = ?, cost_centre_associated = ?, 
                is_inactive = ?, is_active = ?
            WHERE id = ?
            """,
            (
                account_number.strip(), account_name.strip(), account_type.strip(), 
                financial_statement.strip(), normal_balance.strip(),
                account_group.strip() if account_group else None,
                account_class.strip() if account_class else "POSTING",
                posting_form.strip() if posting_form else "DETAILED",
                1 if maintain_quantity else 0,
                1 if cost_centre_associated else 0,
                1 if is_inactive else 0,
                0 if is_inactive else 1,
                account_id
            )
        )


    # =========================================================================
    # 2. GL Company Mappings
    # =========================================================================
    @staticmethod
    def get_mappings_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT m.*, a.account_number, a.account_name, a.account_type, a.normal_balance, c.name AS company_name, c.short_code AS company_code
            FROM gl_company_mappings m
            JOIN gl_accounts a ON m.gl_account_id = a.id
            JOIN companies c ON m.company_id = c.id
            WHERE m.company_id = ? AND COALESCE(m.isDelete, 0) = 0
            ORDER BY a.account_number ASC
            """,
            (company_id,)
        )

    @staticmethod
    def get_mapping_by_id(mapping_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT m.*, a.account_number, a.account_name, c.short_code AS company_code
            FROM gl_company_mappings m
            JOIN gl_accounts a ON m.gl_account_id = a.id
            JOIN companies c ON m.company_id = c.id
            WHERE m.id = ? AND COALESCE(m.isDelete, 0) = 0
            """,
            (mapping_id,)
        )

    @staticmethod
    def get_company_mappings_matrix(gl_account_id: str) -> List[Dict[str, Any]]:
        """Returns mapping state across ALL conglomerate subsidiaries for a specific GL account."""
        sql = """
            SELECT 
                c.id AS company_id,
                c.short_code AS company_code,
                c.name AS company_name,
                c.currency AS base_currency,
                m.id AS mapping_id,
                m.company_account_alias,
                COALESCE(m.posting_currency, c.currency) AS posting_currency,
                COALESCE(m.allow_direct_posting, 1) AS allow_direct_posting,
                CASE WHEN m.id IS NOT NULL AND COALESCE(m.is_enabled, 1) = 1 AND COALESCE(m.isDelete, 0) = 0 THEN 1 ELSE 0 END AS is_mapped
            FROM companies c
            LEFT JOIN gl_company_mappings m ON c.id = m.company_id AND m.gl_account_id = ? AND COALESCE(m.isDelete, 0) = 0
            WHERE c.is_active = 1
            ORDER BY c.sort_order ASC, c.short_code ASC
        """
        return db.query(sql, (gl_account_id,))

    @staticmethod
    def save_company_mappings_matrix(gl_account_id: str, mappings_data: List[Dict[str, Any]]) -> None:
        """Batch saves/updates subsidiary mappings for an account."""
        for item in mappings_data:
            cid = item.get("company_id")
            is_mapped = bool(item.get("is_mapped"))
            alias = item.get("company_account_alias") or ""
            curr = item.get("posting_currency") or "USD"
            allow_posting = 1 if item.get("allow_direct_posting", True) else 0

            existing = db.query_one(
                "SELECT id FROM gl_company_mappings WHERE gl_account_id = ? AND company_id = ?",
                (gl_account_id, cid)
            )
            if existing:
                if is_mapped:
                    db.execute(
                        """
                        UPDATE gl_company_mappings 
                        SET company_account_alias = ?, posting_currency = ?, allow_direct_posting = ?, is_enabled = 1, isDelete = 0
                        WHERE id = ?
                        """,
                        (alias.strip() if alias else None, curr.strip(), allow_posting, existing["id"])
                    )
                else:
                    db.execute(
                        "UPDATE gl_company_mappings SET is_enabled = 0, isDelete = 1 WHERE id = ?",
                        (existing["id"],)
                    )
            elif is_mapped:
                db.execute(
                    """
                    INSERT INTO gl_company_mappings (gl_account_id, company_id, company_account_alias, allow_direct_posting, posting_currency, is_enabled, isDelete)
                    VALUES (?, ?, ?, ?, ?, 1, 0)
                    """,
                    (gl_account_id, cid, alias.strip() if alias else None, allow_posting, curr.strip())
                )

    @staticmethod
    def create_company_mapping(gl_account_id: str, company_id: str, alias: str, currency: str, allow_direct_posting: bool = True) -> None:
        db.execute(
            """
            INSERT INTO gl_company_mappings (gl_account_id, company_id, company_account_alias, allow_direct_posting, posting_currency, is_enabled, isDelete)
            VALUES (?, ?, ?, ?, ?, 1, 0)
            """,
            (gl_account_id, company_id, alias.strip() if alias else None, 1 if allow_direct_posting else 0, currency.strip())
        )

    @staticmethod
    def update_company_mapping(mapping_id: str, gl_account_id: str, company_id: str, alias: str, currency: str, allow_direct_posting: bool = True) -> None:
        db.execute(
            """
            UPDATE gl_company_mappings 
            SET gl_account_id = ?, company_id = ?, company_account_alias = ?, posting_currency = ?, allow_direct_posting = ?
            WHERE id = ?
            """,
            (gl_account_id, company_id, alias.strip() if alias else None, currency.strip(), 1 if allow_direct_posting else 0, mapping_id)
        )

    # =========================================================================
    # 3. GL Sub Accounts
    # =========================================================================
    @staticmethod
    def get_all_sub_accounts() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT s.*, a.account_number AS parent_account_number, a.account_name AS parent_account_name
            FROM gl_sub_accounts s
            JOIN gl_accounts a ON s.gl_account_id = a.id
            WHERE COALESCE(s.isDelete, 0) = 0
            ORDER BY s.sub_account_code ASC
            """
        )

    @staticmethod
    def get_sub_account_by_id(sub_account_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT s.*, a.account_number AS parent_account_number, a.account_name AS parent_account_name
            FROM gl_sub_accounts s
            JOIN gl_accounts a ON s.gl_account_id = a.id
            WHERE s.id = ? AND COALESCE(s.isDelete, 0) = 0
            """,
            (sub_account_id,)
        )

    @staticmethod
    def create_sub_account(gl_account_id: str, sub_account_code: str, sub_account_name: str, sub_account_type: str, description: Optional[str] = None, is_active: bool = True) -> None:
        db.execute(
            """
            INSERT INTO gl_sub_accounts (gl_account_id, sub_account_code, sub_account_name, sub_account_type, description, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (gl_account_id, sub_account_code.strip(), sub_account_name.strip(), sub_account_type.strip(), description.strip() if description else None, 1 if is_active else 0)
        )

    @staticmethod
    def update_sub_account(sub_account_id: str, gl_account_id: str, sub_account_code: str, sub_account_name: str, sub_account_type: str, description: Optional[str] = None, is_active: bool = True) -> None:
        db.execute(
            """
            UPDATE gl_sub_accounts 
            SET gl_account_id = ?, sub_account_code = ?, sub_account_name = ?, sub_account_type = ?, description = ?, is_active = ?
            WHERE id = ?
            """,
            (gl_account_id, sub_account_code.strip(), sub_account_name.strip(), sub_account_type.strip(), description.strip() if description else None, 1 if is_active else 0, sub_account_id)
        )

    # =========================================================================
    # 4. Departments
    # =========================================================================
    @staticmethod
    def get_all_departments() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM gl_departments WHERE COALESCE(isDelete, 0) = 0 ORDER BY dept_code ASC")

    @staticmethod
    def get_department_by_id(department_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM gl_departments WHERE id = ? AND COALESCE(isDelete, 0) = 0", (department_id,))

    @staticmethod
    def create_department(dept_code: str, dept_name: str, head_of_dept: str) -> None:
        db.execute(
            """
            INSERT INTO gl_departments (dept_code, dept_name, head_of_dept, is_active, isDelete)
            VALUES (?, ?, ?, 1, 0)
            """,
            (dept_code.strip(), dept_name.strip(), head_of_dept.strip() if head_of_dept else None)
        )

    @staticmethod
    def update_department(department_id: str, dept_code: str, dept_name: str, head_of_dept: str) -> None:
        db.execute(
            """
            UPDATE gl_departments 
            SET dept_code = ?, dept_name = ?, head_of_dept = ?
            WHERE id = ?
            """,
            (dept_code.strip(), dept_name.strip(), head_of_dept.strip() if head_of_dept else None, department_id)
        )

    # =========================================================================
    # 5. Cost Centres (Unified on Authoritative admin_cost_centers Master)
    # =========================================================================
    @staticmethod
    def get_cost_centres_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT cc.id, cc.code, cc.company_id, cc.business_unit_id,
                   cc.cost_center_code, cc.cost_center_code AS cost_centre_code,
                   cc.name AS cost_centre_name, cc.name, cc.department, cc.manager_name,
                   cc.is_profit_center, cc.budget_allocation, cc.is_active,
                   c.short_code AS company_code
            FROM admin_cost_centers cc
            JOIN companies c ON cc.company_id = c.id
            WHERE cc.company_id = ?
            ORDER BY cc.cost_center_code ASC
            """,
            (company_id,)
        )

    @staticmethod
    def get_cost_centre_by_id(cost_centre_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT cc.id, cc.code, cc.company_id, cc.business_unit_id,
                   cc.cost_center_code, cc.cost_center_code AS cost_centre_code,
                   cc.name AS cost_centre_name, cc.name, cc.department, cc.manager_name,
                   cc.is_profit_center, cc.budget_allocation, cc.is_active,
                   c.short_code AS company_code
            FROM admin_cost_centers cc
            JOIN companies c ON cc.company_id = c.id
            WHERE cc.id = ?
            """,
            (cost_centre_id,)
        )

    @staticmethod
    def create_cost_centre(cost_centre_code: str, cost_centre_name: str, department_id: Optional[str], company_id: str) -> None:
        bu = db.query_one("SELECT TOP 1 id FROM admin_business_units WHERE company_id = ?", (company_id,))
        bu_id = bu["id"] if bu else None
        db.execute(
            """
            INSERT INTO admin_cost_centers (id, company_id, business_unit_id, cost_center_code, name, department, manager_name, is_profit_center, budget_allocation, is_active)
            VALUES (NEWID(), ?, ?, ?, ?, 'General Ledger CC', 'Finance Lead', 0, 500000.00, 1)
            """,
            (company_id, bu_id, cost_centre_code.strip(), cost_centre_name.strip())
        )

    @staticmethod
    def update_cost_centre(cost_centre_id: str, cost_centre_code: str, cost_centre_name: str, department_id: Optional[str], company_id: str) -> None:
        db.execute(
            """
            UPDATE admin_cost_centers 
            SET cost_center_code = ?, name = ?, company_id = ?
            WHERE id = ?
            """,
            (cost_centre_code.strip(), cost_centre_name.strip(), company_id, cost_centre_id)
        )

    # =========================================================================
    # 6. Budget Sets
    # =========================================================================
    @staticmethod
    def get_budgets_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, a.account_number, a.account_name, 
                   cc.cost_center_code AS cost_centre_code, cc.name AS cost_centre_name, 
                   c.short_code AS company_code
            FROM gl_budget_sets b
            JOIN gl_accounts a ON b.gl_account_id = a.id
            LEFT JOIN admin_cost_centers cc ON b.cost_centre_id = cc.id
            JOIN companies c ON b.company_id = c.id
            WHERE b.company_id = ? AND COALESCE(b.isDelete, 0) = 0
            ORDER BY b.budget_code ASC
            """,
            (company_id,)
        )

    @staticmethod
    def get_budget_set_by_id(budget_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT b.*, a.account_number, a.account_name, 
                   cc.cost_center_code AS cost_centre_code, cc.name AS cost_centre_name, 
                   c.short_code AS company_code
            FROM gl_budget_sets b
            JOIN gl_accounts a ON b.gl_account_id = a.id
            LEFT JOIN admin_cost_centers cc ON b.cost_centre_id = cc.id
            JOIN companies c ON b.company_id = c.id
            WHERE b.id = ? AND COALESCE(b.isDelete, 0) = 0
            """,
            (budget_id,)
        )

    @staticmethod
    def create_budget_set(
        budget_code: str, 
        budget_title: str, 
        fiscal_year: str, 
        company_id: str, 
        cost_centre_id: Optional[str], 
        gl_account_id: str, 
        allocated_amount: float, 
        status: str = "APPROVED",
        description: Optional[str] = None,
        is_locked: bool = False
    ) -> None:
        db.execute(
            """
            INSERT INTO gl_budget_sets (
                budget_code, budget_title, fiscal_year, company_id, cost_centre_id, 
                gl_account_id, allocated_amount, utilized_amount, status, description, is_locked, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, ?, ?, ?, 0)
            """,
            (
                budget_code.strip(), budget_title.strip(), fiscal_year.strip(), company_id, 
                cost_centre_id if cost_centre_id else None, gl_account_id, allocated_amount, 
                status.strip(), description.strip() if description else None, 1 if is_locked else 0
            )
        )

    @staticmethod
    def update_budget_set(
        budget_id: str, 
        budget_title: str, 
        fiscal_year: str, 
        company_id: str, 
        cost_centre_id: Optional[str], 
        gl_account_id: str, 
        allocated_amount: float, 
        status: str = "APPROVED",
        description: Optional[str] = None,
        is_locked: bool = False
    ) -> None:
        db.execute(
            """
            UPDATE gl_budget_sets 
            SET budget_title = ?, fiscal_year = ?, company_id = ?, cost_centre_id = ?, 
                gl_account_id = ?, allocated_amount = ?, status = ?, description = ?, is_locked = ?
            WHERE id = ?
            """,
            (
                budget_title.strip(), fiscal_year.strip(), company_id, 
                cost_centre_id if cost_centre_id else None, gl_account_id, allocated_amount, 
                status.strip(), description.strip() if description else None, 1 if is_locked else 0, 
                budget_id
            )
        )

    @staticmethod
    def is_budget_locked(budget_id: str) -> bool:
        row = db.query_one("SELECT is_locked FROM gl_budget_sets WHERE id = ?", (budget_id,))
        return bool(row and row.get("is_locked"))

    # =========================================================================
    # Safe Soft-Delete Operations for GL Master Entities (isDelete & isDeleteDate)
    # =========================================================================
    @staticmethod
    def delete_entity_record(entity: str, record_id: str) -> bool:
        entity_table_map = {
            "gl-accounts": "gl_accounts",
            "company-mappings": "gl_company_mappings",
            "sub-accounts": "gl_sub_accounts",
            "departments": "gl_departments",
            "cost-centres": "admin_cost_centers",
            "budget-sets": "gl_budget_sets",
        }
        table_name = entity_table_map.get(entity)
        if not table_name:
            return False
        
        try:
            valid_uuid = str(uuid.UUID(str(record_id)))
            db.execute(f"UPDATE {table_name} SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (valid_uuid,))
            return True
        except (ValueError, Exception):
            return False
