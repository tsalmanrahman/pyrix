from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class GLCategoryService:
    """
    Service managing Statutory Account Categories and IFRS 8 Operating Segments
    for the General Ledger Enterprise Module.
    """

    # =========================================================================
    # 1. Statutory Account Categories
    # =========================================================================
    @staticmethod
    def get_categories(statement_section: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves all active statutory categories along with the count of 
        currently mapped Chart of Accounts items.
        """
        sql = """
            SELECT 
                c.id,
                c.code,
                c.category_code,
                c.category_name,
                c.description,
                c.statement_section,
                c.classification_type,
                c.reporting_sort,
                c.is_active,
                c.created_at,
                COUNT(a.id) AS mapped_accounts_count
            FROM gl_account_categories c
            LEFT JOIN gl_accounts a ON a.category_id = c.id AND COALESCE(a.isDelete, 0) = 0
            WHERE COALESCE(c.isDelete, 0) = 0
        """
        params = []
        if statement_section and statement_section != "ALL":
            sql += " AND c.statement_section = ?"
            params.append(statement_section)

        sql += """
            GROUP BY 
                c.id, c.code, c.category_code, c.category_name, c.description,
                c.statement_section, c.classification_type, c.reporting_sort,
                c.is_active, c.created_at
            ORDER BY c.reporting_sort ASC, c.category_code ASC
        """
        return db.query(sql, tuple(params))

    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a single statutory category and its associated Chart of Accounts entries.
        """
        cat = db.query_one("""
            SELECT * FROM gl_account_categories 
            WHERE id = ? AND COALESCE(isDelete, 0) = 0
        """, (category_id,))
        if not cat:
            return None

        # Attach linked accounts
        cat['accounts'] = db.query("""
            SELECT id, account_number, account_name, account_type, financial_statement, normal_balance, is_active
            FROM gl_accounts 
            WHERE category_id = ? AND COALESCE(isDelete, 0) = 0
            ORDER BY account_number ASC
        """, (category_id,))
        return cat

    @staticmethod
    def is_category_code_unique(category_code: str, exclude_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        sql = "SELECT id, category_code, category_name FROM gl_account_categories WHERE LOWER(TRIM(category_code)) = LOWER(TRIM(?)) AND COALESCE(isDelete, 0) = 0"
        params = [category_code]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        row = db.query_one(sql, tuple(params))
        if row:
            return False, row.get("category_code")
        return True, None

    @staticmethod
    def is_category_name_unique(category_name: str, exclude_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        sql = "SELECT id, category_code, category_name FROM gl_account_categories WHERE LOWER(TRIM(category_name)) = LOWER(TRIM(?)) AND COALESCE(isDelete, 0) = 0"
        params = [category_name]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        row = db.query_one(sql, tuple(params))
        if row:
            return False, row.get("category_code")
        return True, None

    @staticmethod
    def create_category(
        category_code: str,
        category_name: str,
        statement_section: str,
        classification_type: str,
        description: Optional[str] = None,
        reporting_sort: int = 10
    ) -> str:
        code_unique, existing_code = GLCategoryService.is_category_code_unique(category_code)
        if not code_unique:
            raise ValueError(f"Category Code '{category_code.strip()}' already exists.")

        name_unique, existing_code = GLCategoryService.is_category_name_unique(category_name)
        if not name_unique:
            raise ValueError(f"Category Name '{category_name.strip()}' already exists (Code: {existing_code}).")

        cat_id = str(uuid.uuid4())
        max_code_row = db.query_one("SELECT COALESCE(MAX(code), 0) + 1 AS next_code FROM gl_account_categories")
        next_code = max_code_row['next_code'] if max_code_row else 1

        db.execute("""
            INSERT INTO gl_account_categories (
                id, code, category_code, category_name, description,
                statement_section, classification_type, reporting_sort,
                is_active, created_at, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), 0)
        """, (
            cat_id,
            next_code,
            category_code.strip().upper(),
            category_name.strip(),
            (description or '').strip(),
            statement_section.strip().upper(),
            classification_type.strip().upper(),
            reporting_sort
        ))
        return cat_id

    @staticmethod
    def update_category(
        category_id: str,
        category_name: str,
        statement_section: str,
        classification_type: str,
        description: Optional[str] = None,
        reporting_sort: int = 10,
        is_active: bool = True
    ) -> None:
        name_unique, existing_code = GLCategoryService.is_category_name_unique(category_name, exclude_id=category_id)
        if not name_unique:
            raise ValueError(f"Category Name '{category_name.strip()}' already exists (Code: {existing_code}).")

        db.execute("""
            UPDATE gl_account_categories
            SET category_name = ?,
                statement_section = ?,
                classification_type = ?,
                description = ?,
                reporting_sort = ?,
                is_active = ?
            WHERE id = ? AND COALESCE(isDelete, 0) = 0
        """, (
            category_name.strip(),
            statement_section.strip().upper(),
            classification_type.strip().upper(),
            (description or '').strip(),
            reporting_sort,
            1 if is_active else 0,
            category_id
        ))


    @staticmethod
    def delete_category(category_id: str) -> None:
        db.execute("""
            UPDATE gl_account_categories
            SET isDelete = 1
            WHERE id = ?
        """, (category_id,))
        # Unlink accounts that were assigned to this category
        db.execute("""
            UPDATE gl_accounts
            SET category_id = NULL
            WHERE category_id = ?
        """, (category_id,))

    # =========================================================================
    # 2. IFRS 8 Financial Segments
    # =========================================================================
    @staticmethod
    def get_segments() -> List[Dict[str, Any]]:
        """
        Retrieves all operating financial segments.
        """
        return db.query("""
            SELECT * FROM gl_financial_segments
            WHERE COALESCE(isDelete, 0) = 0
            ORDER BY code ASC, segment_code ASC
        """)

    @staticmethod
    def get_segment_by_id(segment_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("""
            SELECT * FROM gl_financial_segments
            WHERE id = ? AND COALESCE(isDelete, 0) = 0
        """, (segment_id,))

    @staticmethod
    def is_segment_code_unique(segment_code: str, exclude_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        sql = "SELECT id, segment_code, segment_name FROM gl_financial_segments WHERE LOWER(TRIM(segment_code)) = LOWER(TRIM(?)) AND COALESCE(isDelete, 0) = 0"
        params = [segment_code]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        row = db.query_one(sql, tuple(params))
        if row:
            return False, row.get("segment_code")
        return True, None

    @staticmethod
    def is_segment_name_unique(segment_name: str, exclude_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        sql = "SELECT id, segment_code, segment_name FROM gl_financial_segments WHERE LOWER(TRIM(segment_name)) = LOWER(TRIM(?)) AND COALESCE(isDelete, 0) = 0"
        params = [segment_name]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        row = db.query_one(sql, tuple(params))
        if row:
            return False, row.get("segment_code")
        return True, None

    @staticmethod
    def create_segment(
        segment_code: str,
        segment_name: str,
        segment_type: str,
        head_of_segment: Optional[str] = None,
        target_margin_pct: float = 0.0,
        revenue_weight_pct: float = 0.0
    ) -> str:
        code_unique, existing_code = GLCategoryService.is_segment_code_unique(segment_code)
        if not code_unique:
            raise ValueError(f"Segment Code '{segment_code.strip()}' already exists.")

        name_unique, existing_code = GLCategoryService.is_segment_name_unique(segment_name)
        if not name_unique:
            raise ValueError(f"Segment Name '{segment_name.strip()}' already exists (Code: {existing_code}).")

        seg_id = str(uuid.uuid4())
        max_code_row = db.query_one("SELECT COALESCE(MAX(code), 0) + 1 AS next_code FROM gl_financial_segments")
        next_code = max_code_row['next_code'] if max_code_row else 1

        db.execute("""
            INSERT INTO gl_financial_segments (
                id, code, segment_code, segment_name, segment_type,
                head_of_segment, target_margin_pct, revenue_weight_pct,
                is_active, created_at, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), 0)
        """, (
            seg_id,
            next_code,
            segment_code.strip().upper(),
            segment_name.strip(),
            segment_type.strip(),
            (head_of_segment or '').strip(),
            float(target_margin_pct),
            float(revenue_weight_pct)
        ))
        return seg_id

    @staticmethod
    def update_segment(
        segment_id: str,
        segment_name: str,
        segment_type: str,
        head_of_segment: Optional[str] = None,
        target_margin_pct: float = 0.0,
        revenue_weight_pct: float = 0.0,
        is_active: bool = True
    ) -> None:
        name_unique, existing_code = GLCategoryService.is_segment_name_unique(segment_name, exclude_id=segment_id)
        if not name_unique:
            raise ValueError(f"Segment Name '{segment_name.strip()}' already exists (Code: {existing_code}).")

        db.execute("""
            UPDATE gl_financial_segments
            SET segment_name = ?,
                segment_type = ?,
                head_of_segment = ?,
                target_margin_pct = ?,
                revenue_weight_pct = ?,
                is_active = ?
            WHERE id = ? AND COALESCE(isDelete, 0) = 0
        """, (
            segment_name.strip(),
            segment_type.strip(),
            (head_of_segment or '').strip(),
            float(target_margin_pct),
            float(revenue_weight_pct),
            1 if is_active else 0,
            segment_id
        ))


    @staticmethod
    def delete_segment(segment_id: str) -> None:
        db.execute("""
            UPDATE gl_financial_segments
            SET isDelete = 1
            WHERE id = ?
        """, (segment_id,))

    # =========================================================================
    # 3. Studio Aggregate KPIs
    # =========================================================================
    @staticmethod
    def get_summary_kpis() -> Dict[str, Any]:
        """
        Computes real-time analytical KPIs for the Studio top stats banner.
        """
        categories = GLCategoryService.get_categories()
        segments = GLCategoryService.get_segments()

        bs_count = sum(1 for c in categories if c.get('statement_section') == 'BALANCE_SHEET')
        is_count = sum(1 for c in categories if c.get('statement_section') == 'INCOME_STATEMENT')
        mapped_total = sum(c.get('mapped_accounts_count', 0) for c in categories)
        
        avg_margin = 0.0
        if segments:
            margins = [float(s.get('target_margin_pct', 0) or 0) for s in segments]
            avg_margin = round(sum(margins) / len(margins), 1)

        return {
            "total_categories": len(categories),
            "balance_sheet_categories": bs_count,
            "income_statement_categories": is_count,
            "total_segments": len(segments),
            "average_segment_margin": avg_margin,
            "mapped_accounts_total": mapped_total
        }
