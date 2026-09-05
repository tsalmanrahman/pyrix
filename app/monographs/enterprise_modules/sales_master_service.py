from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class SalesMasterService:

    # =========================================================================
    # 1. SALES AREAS & TERRITORIES
    # =========================================================================
    @staticmethod
    def get_sales_areas(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT a.*, c.name AS company_name, c.short_code AS company_code,
                       (SELECT COUNT(*) FROM sales_teams t WHERE t.area_id = a.id) AS team_count
                FROM sales_areas a
                JOIN companies c ON a.company_id = c.id
                WHERE a.company_id = ? AND a.is_active = 1
                ORDER BY a.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT a.*, c.name AS company_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM sales_teams t WHERE t.area_id = a.id) AS team_count
            FROM sales_areas a
            JOIN companies c ON a.company_id = c.id
            WHERE a.is_active = 1
            ORDER BY c.sort_order ASC, a.code ASC
            """
        )

    @staticmethod
    def create_sales_area(company_id: str, area_code: str, area_name: str, region_name: str, head_of_area: str) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sales_areas (id, company_id, area_code, area_name, region_name, head_of_area, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, company_id, area_code.strip(), area_name.strip(), region_name.strip(), head_of_area.strip())
        )
        return new_id

    # =========================================================================
    # 2. SALES TEAMS (MM > ZM > TSM Hierarchy)
    # =========================================================================
    @staticmethod
    def get_sales_teams(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT t.*, a.area_name, a.region_name, c.short_code AS company_code,
                       (SELECT COUNT(*) FROM salespersons sp WHERE sp.team_id = t.id) AS member_count
                FROM sales_teams t
                JOIN companies c ON t.company_id = c.id
                LEFT JOIN sales_areas a ON t.area_id = a.id
                WHERE t.company_id = ? AND t.is_active = 1
                ORDER BY t.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT t.*, a.area_name, a.region_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM salespersons sp WHERE sp.team_id = t.id) AS member_count
            FROM sales_teams t
            JOIN companies c ON t.company_id = c.id
            LEFT JOIN sales_areas a ON t.area_id = a.id
            WHERE t.is_active = 1
            ORDER BY c.sort_order ASC, t.code ASC
            """
        )

    @staticmethod
    def create_sales_team(company_id: str, area_id: Optional[str], team_code: str, team_name: str, team_type: str, manager_name: str, target_annual_amount: float = 0.0) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sales_teams (id, company_id, area_id, team_code, team_name, team_type, manager_name, target_annual_amount, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, company_id, area_id, team_code.strip(), team_name.strip(), team_type, manager_name.strip(), target_annual_amount)
        )
        return new_id

    # =========================================================================
    # 3. SALESPERSONS MASTER
    # =========================================================================
    @staticmethod
    def get_salespersons(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT sp.*, t.team_name, t.team_code, c.short_code AS company_code,
                       (SELECT COUNT(*) FROM sales_orders so WHERE so.salesperson_id = sp.id) AS order_count,
                       (SELECT ISNULL(SUM(so.total_amount), 0) FROM sales_orders so WHERE so.salesperson_id = sp.id) AS total_sold_amount
                FROM salespersons sp
                JOIN companies c ON sp.company_id = c.id
                LEFT JOIN sales_teams t ON sp.team_id = t.id
                WHERE sp.company_id = ? AND sp.is_active = 1
                ORDER BY sp.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT sp.*, t.team_name, t.team_code, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM sales_orders so WHERE so.salesperson_id = sp.id) AS order_count,
                   (SELECT ISNULL(SUM(so.total_amount), 0) FROM sales_orders so WHERE so.salesperson_id = sp.id) AS total_sold_amount
            FROM salespersons sp
            JOIN companies c ON sp.company_id = c.id
            LEFT JOIN sales_teams t ON sp.team_id = t.id
            WHERE sp.is_active = 1
            ORDER BY c.sort_order ASC, sp.code ASC
            """
        )

    @staticmethod
    def create_salesperson(company_id: str, team_id: Optional[str], salesperson_code: str, full_name: str, email: str, phone: str, designation: str, max_discount_pct: float = 5.0, monthly_target: float = 50000.0, commission_pct: float = 2.5) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO salespersons (id, company_id, team_id, salesperson_code, full_name, email, phone, designation, max_discount_pct, monthly_target, commission_pct, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, company_id, team_id, salesperson_code.strip(), full_name.strip(), email.strip(), phone.strip(), designation.strip(), max_discount_pct, monthly_target, commission_pct)
        )
        return new_id

    # =========================================================================
    # 4. PRICE PROFILES & PRICE CATALOGS
    # =========================================================================
    @staticmethod
    def get_price_profiles(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT pp.*, c.short_code AS company_code,
                       (SELECT COUNT(*) FROM sales_product_prices pr WHERE pr.profile_id = pp.id) AS item_count
                FROM sales_price_profiles pp
                JOIN companies c ON pp.company_id = c.id
                WHERE pp.company_id = ? AND pp.is_active = 1
                ORDER BY pp.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT pp.*, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM sales_product_prices pr WHERE pr.profile_id = pp.id) AS item_count
            FROM sales_price_profiles pp
            JOIN companies c ON pp.company_id = c.id
            WHERE pp.is_active = 1
            ORDER BY c.sort_order ASC, pp.code ASC
            """
        )

    @staticmethod
    def get_product_prices(profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if profile_id:
            return db.query(
                """
                SELECT pr.*, pp.profile_code, pp.profile_name, pp.currency
                FROM sales_product_prices pr
                JOIN sales_price_profiles pp ON pr.profile_id = pp.id
                WHERE pr.profile_id = ? AND pr.is_active = 1
                ORDER BY pr.code ASC
                """,
                (profile_id,)
            )
        return db.query(
            """
            SELECT pr.*, pp.profile_code, pp.profile_name, pp.currency
            FROM sales_product_prices pr
            JOIN sales_price_profiles pp ON pr.profile_id = pp.id
            WHERE pr.is_active = 1
            ORDER BY pp.profile_code ASC, pr.code ASC
            """
        )

    @staticmethod
    def create_price_profile(company_id: str, profile_code: str, profile_name: str, currency: str = "USD", price_type: str = "BASE_PRICE", is_default: int = 0) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sales_price_profiles (id, company_id, profile_code, profile_name, currency, price_type, is_default, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, company_id, profile_code.strip(), profile_name.strip(), currency, price_type, is_default)
        )
        return new_id

    # =========================================================================
    # 5. DISCOUNT LIMITS MATRIX
    # =========================================================================
    @staticmethod
    def get_discount_limits() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM sales_discount_limits WHERE is_active = 1 ORDER BY max_discount_pct ASC")
