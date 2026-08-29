from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class GLMasterService:

    # =========================================================================
    # 1. GL Accounts (Chart of Accounts)
    # =========================================================================
    @staticmethod
    def get_all_accounts() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM gl_accounts WHERE COALESCE(isDelete, 0) = 0 ORDER BY account_number ASC")

    @staticmethod
    def get_account_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM gl_accounts WHERE id = ? AND COALESCE(isDelete, 0) = 0", (account_id,))

    @staticmethod
    def create_account(account_number: str, account_name: str, account_type: str, financial_statement: str, normal_balance: str) -> None:
        db.execute(
            """
            INSERT INTO gl_accounts (account_number, account_name, account_type, financial_statement, normal_balance, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, 1, 0)
            """,
            (account_number.strip(), account_name.strip(), account_type.strip(), financial_statement.strip(), normal_balance.strip())
        )

    @staticmethod
    def update_account(account_id: str, account_number: str, account_name: str, account_type: str, financial_statement: str, normal_balance: str) -> None:
        db.execute(
            """
            UPDATE gl_accounts 
            SET account_number = ?, account_name = ?, account_type = ?, financial_statement = ?, normal_balance = ?
            WHERE id = ?
            """,
            (account_number.strip(), account_name.strip(), account_type.strip(), financial_statement.strip(), normal_balance.strip(), account_id)
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
    def create_company_mapping(gl_account_id: str, company_id: str, alias: str, currency: str) -> None:
        db.execute(
            """
            INSERT INTO gl_company_mappings (gl_account_id, company_id, company_account_alias, allow_direct_posting, posting_currency, is_enabled, isDelete)
            VALUES (?, ?, ?, 1, ?, 1, 0)
            """,
            (gl_account_id, company_id, alias.strip() if alias else None, currency.strip())
        )

    @staticmethod
    def update_company_mapping(mapping_id: str, gl_account_id: str, company_id: str, alias: str, currency: str) -> None:
        db.execute(
            """
            UPDATE gl_company_mappings 
            SET gl_account_id = ?, company_id = ?, company_account_alias = ?, posting_currency = ?
            WHERE id = ?
            """,
            (gl_account_id, company_id, alias.strip() if alias else None, currency.strip(), mapping_id)
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
    def create_sub_account(gl_account_id: str, sub_account_code: str, sub_account_name: str, sub_account_type: str) -> None:
        db.execute(
            """
            INSERT INTO gl_sub_accounts (gl_account_id, sub_account_code, sub_account_name, sub_account_type, is_active, isDelete)
            VALUES (?, ?, ?, ?, 1, 0)
            """,
            (gl_account_id, sub_account_code.strip(), sub_account_name.strip(), sub_account_type.strip())
        )

    @staticmethod
    def update_sub_account(sub_account_id: str, gl_account_id: str, sub_account_code: str, sub_account_name: str, sub_account_type: str) -> None:
        db.execute(
            """
            UPDATE gl_sub_accounts 
            SET gl_account_id = ?, sub_account_code = ?, sub_account_name = ?, sub_account_type = ?
            WHERE id = ?
            """,
            (gl_account_id, sub_account_code.strip(), sub_account_name.strip(), sub_account_type.strip(), sub_account_id)
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
    # 5. Cost Centres
    # =========================================================================
    @staticmethod
    def get_cost_centres_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT cc.*, d.dept_code, d.dept_name, c.short_code AS company_code
            FROM gl_cost_centres cc
            LEFT JOIN gl_departments d ON cc.department_id = d.id
            JOIN companies c ON cc.company_id = c.id
            WHERE cc.company_id = ? AND COALESCE(cc.isDelete, 0) = 0
            ORDER BY cc.cost_centre_code ASC
            """,
            (company_id,)
        )

    @staticmethod
    def get_cost_centre_by_id(cost_centre_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT cc.*, d.dept_code, d.dept_name, c.short_code AS company_code
            FROM gl_cost_centres cc
            LEFT JOIN gl_departments d ON cc.department_id = d.id
            JOIN companies c ON cc.company_id = c.id
            WHERE cc.id = ? AND COALESCE(cc.isDelete, 0) = 0
            """,
            (cost_centre_id,)
        )

    @staticmethod
    def create_cost_centre(cost_centre_code: str, cost_centre_name: str, department_id: Optional[str], company_id: str) -> None:
        db.execute(
            """
            INSERT INTO gl_cost_centres (cost_centre_code, cost_centre_name, department_id, company_id, is_active, isDelete)
            VALUES (?, ?, ?, ?, 1, 0)
            """,
            (cost_centre_code.strip(), cost_centre_name.strip(), department_id if department_id else None, company_id)
        )

    @staticmethod
    def update_cost_centre(cost_centre_id: str, cost_centre_code: str, cost_centre_name: str, department_id: Optional[str], company_id: str) -> None:
        db.execute(
            """
            UPDATE gl_cost_centres 
            SET cost_centre_code = ?, cost_centre_name = ?, department_id = ?, company_id = ?
            WHERE id = ?
            """,
            (cost_centre_code.strip(), cost_centre_name.strip(), department_id if department_id else None, company_id, cost_centre_id)
        )

    # =========================================================================
    # 6. Budget Sets
    # =========================================================================
    @staticmethod
    def get_budgets_for_company(company_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, a.account_number, a.account_name, cc.cost_centre_code, cc.cost_centre_name, c.short_code AS company_code
            FROM gl_budget_sets b
            JOIN gl_accounts a ON b.gl_account_id = a.id
            LEFT JOIN gl_cost_centres cc ON b.cost_centre_id = cc.id
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
            SELECT b.*, a.account_number, a.account_name, cc.cost_centre_code, cc.cost_centre_name, c.short_code AS company_code
            FROM gl_budget_sets b
            JOIN gl_accounts a ON b.gl_account_id = a.id
            LEFT JOIN gl_cost_centres cc ON b.cost_centre_id = cc.id
            JOIN companies c ON b.company_id = c.id
            WHERE b.id = ? AND COALESCE(b.isDelete, 0) = 0
            """,
            (budget_id,)
        )

    @staticmethod
    def create_budget_set(budget_code: str, budget_title: str, fiscal_year: str, company_id: str, cost_centre_id: Optional[str], gl_account_id: str, allocated_amount: float, status: str = "APPROVED") -> None:
        db.execute(
            """
            INSERT INTO gl_budget_sets (budget_code, budget_title, fiscal_year, company_id, cost_centre_id, gl_account_id, allocated_amount, utilized_amount, status, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, ?, 0)
            """,
            (budget_code.strip(), budget_title.strip(), fiscal_year.strip(), company_id, cost_centre_id if cost_centre_id else None, gl_account_id, allocated_amount, status.strip())
        )

    @staticmethod
    def update_budget_set(budget_id: str, budget_title: str, fiscal_year: str, company_id: str, cost_centre_id: Optional[str], gl_account_id: str, allocated_amount: float, status: str = "APPROVED") -> None:
        db.execute(
            """
            UPDATE gl_budget_sets 
            SET budget_title = ?, fiscal_year = ?, company_id = ?, cost_centre_id = ?, gl_account_id = ?, allocated_amount = ?, status = ?
            WHERE id = ?
            """,
            (budget_title.strip(), fiscal_year.strip(), company_id, cost_centre_id if cost_centre_id else None, gl_account_id, allocated_amount, status.strip(), budget_id)
        )

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
            "cost-centres": "gl_cost_centres",
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
