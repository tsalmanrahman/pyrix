from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class SourcingMasterService:

    # =========================================================================
    # 1. VENDOR MASTER PROFILE
    # =========================================================================
    @staticmethod
    def get_all_vendors() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT v.*,
                   (SELECT COUNT(*) FROM sourcing_purchase_orders po WHERE po.vendor_id = v.id) AS po_count,
                   (SELECT COUNT(*) FROM sourcing_vendor_enlistments e WHERE e.vendor_id = v.id AND e.status = 'ACTIVE') AS active_enlistments
            FROM sourcing_vendors v
            WHERE COALESCE(v.isDelete, 0) = 0
            ORDER BY v.vendor_code ASC
            """
        )

    @staticmethod
    def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT v.*
            FROM sourcing_vendors v
            WHERE v.id = ? AND COALESCE(v.isDelete, 0) = 0
            """,
            (vendor_id,)
        )

    @staticmethod
    def create_vendor(
        vendor_code: str,
        vendor_name: str,
        vendor_group: str = "MANUFACTURER_OEM",
        vendor_org_type: str = "CORPORATE",
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        tax_id_tin: Optional[str] = None,
        vat_bin: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_branch: Optional[str] = None,
        bank_account: Optional[str] = None,
        bank_swift: Optional[str] = None,
        credit_terms_days: int = 30,
        currency: str = "USD",
        rating_stars: float = 4.5
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_vendors 
            (id, vendor_code, vendor_name, vendor_group, vendor_org_type, contact_person, email, phone, address, tax_id_tin, vat_bin, bank_name, bank_branch, bank_account, bank_swift, credit_terms_days, currency, rating_stars, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (new_id, vendor_code.strip(), vendor_name.strip(), vendor_group, vendor_org_type, contact_person, email, phone, address, tax_id_tin, vat_bin, bank_name, bank_branch, bank_account, bank_swift, credit_terms_days, currency, rating_stars)
        )
        return new_id

    @staticmethod
    def update_vendor(
        vendor_id: str,
        vendor_name: str,
        vendor_group: str,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        tax_id_tin: Optional[str] = None,
        vat_bin: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None,
        credit_terms_days: int = 30,
        currency: str = "USD",
        rating_stars: float = 4.5
    ) -> None:
        db.execute(
            """
            UPDATE sourcing_vendors
            SET vendor_name = ?, vendor_group = ?, contact_person = ?, email = ?, phone = ?, address = ?, tax_id_tin = ?, vat_bin = ?, bank_name = ?, bank_account = ?, credit_terms_days = ?, currency = ?, rating_stars = ?
            WHERE id = ?
            """,
            (vendor_name.strip(), vendor_group, contact_person, email, phone, address, tax_id_tin, vat_bin, bank_name, bank_account, credit_terms_days, currency, rating_stars, vendor_id)
        )

    @staticmethod
    def delete_vendor(vendor_id: str) -> None:
        db.execute("UPDATE sourcing_vendors SET isDelete = 1, is_active = 0 WHERE id = ?", (vendor_id,))

    # =========================================================================
    # 2. VENDOR ENLISTMENT & CLASSIFICATION
    # =========================================================================
    @staticmethod
    def get_all_enlistments() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT e.*, v.vendor_code, v.vendor_name, v.vendor_group
            FROM sourcing_vendor_enlistments e
            JOIN sourcing_vendors v ON e.vendor_id = v.id
            WHERE COALESCE(v.isDelete, 0) = 0
            ORDER BY e.valid_to DESC
            """
        )

    @staticmethod
    def create_enlistment(
        vendor_id: str,
        category_name: str,
        enlistment_tier: str = "TIER_1_APPROVED",
        valid_from: str = "2026-01-01",
        valid_to: str = "2026-12-31",
        financial_capacity_usd: float = 500000.0,
        status: str = "ACTIVE",
        inspection_status: str = "VERIFIED_PASSED"
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_vendor_enlistments 
            (id, vendor_id, category_name, enlistment_tier, valid_from, valid_to, financial_capacity_usd, status, inspection_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id, vendor_id, category_name.strip(), enlistment_tier, valid_from, valid_to, financial_capacity_usd, status, inspection_status)
        )
        return new_id

    # =========================================================================
    # 3. SOURCING BUYERS
    # =========================================================================
    @staticmethod
    def get_all_buyers() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, d.dept_code, d.dept_name
            FROM sourcing_buyers b
            LEFT JOIN gl_departments d ON b.department_id = d.id
            ORDER BY b.buyer_code ASC
            """
        )

    @staticmethod
    def create_buyer(
        buyer_code: str,
        buyer_name: str,
        department_id: Optional[str] = None,
        assigned_categories: Optional[str] = None,
        max_approval_limit: float = 50000.0
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_buyers 
            (id, buyer_code, buyer_name, department_id, assigned_categories, max_approval_limit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, buyer_code.strip(), buyer_name.strip(), department_id, assigned_categories, max_approval_limit)
        )
        return new_id

    # =========================================================================
    # 4. PURCHASING ORGANIZATIONS
    # =========================================================================
    @staticmethod
    def get_purchasing_orgs() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT po.*, c.name AS company_name, c.short_code AS company_code
            FROM sourcing_purchasing_orgs po
            LEFT JOIN companies c ON po.company_id = c.id
            ORDER BY po.org_code ASC
            """
        )

    @staticmethod
    def create_purchasing_org(
        org_code: str,
        org_name: str,
        org_type: str = "CENTRAL",
        company_id: Optional[str] = None,
        head_of_procurement: Optional[str] = None
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_purchasing_orgs 
            (id, org_code, org_name, org_type, company_id, head_of_procurement, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, org_code.strip(), org_name.strip(), org_type, company_id, head_of_procurement)
        )
        return new_id

    # =========================================================================
    # 5. SOURCING PRICE TERMS (INCOTERMS & PAYMENT TERMS)
    # =========================================================================
    @staticmethod
    def get_price_terms() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT pt.*
            FROM sourcing_price_terms pt
            ORDER BY pt.term_code ASC
            """
        )

    @staticmethod
    def create_price_term(
        term_code: str,
        term_name: str,
        incoterm: str = "FOB",
        credit_days: int = 30,
        validity_period_months: int = 12,
        description: Optional[str] = None
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_price_terms 
            (id, term_code, term_name, incoterm, credit_days, validity_period_months, description, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, term_code.strip(), term_name.strip(), incoterm, credit_days, validity_period_months, description)
        )
        return new_id

    # =========================================================================
    # 6. C&F AGENTS & INDENTORS
    # =========================================================================
    @staticmethod
    def get_cnf_agents() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT cnf.*,
                   (SELECT COUNT(*) FROM sourcing_cnf_dispatches d WHERE d.cnf_agent_id = cnf.id) AS active_dispatches
            FROM sourcing_cnf_agents cnf
            ORDER BY cnf.agent_code ASC
            """
        )

    @staticmethod
    def create_cnf_agent(
        agent_code: str,
        agent_name: str,
        port_location: str,
        license_number: Optional[str] = None,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        rating_score: float = 4.8
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_cnf_agents 
            (id, agent_code, agent_name, port_location, license_number, contact_person, phone, email, rating_score, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (new_id, agent_code.strip(), agent_name.strip(), port_location.strip(), license_number, contact_person, phone, email, rating_score)
        )
        return new_id

    # =========================================================================
    # 7. MULTI-CURRENCY EXCHANGE RATES
    # =========================================================================
    @staticmethod
    def get_exchange_rates() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM sourcing_exchange_rates ORDER BY foreign_currency ASC")

    @staticmethod
    def update_exchange_rate(foreign_currency: str, exchange_rate: float) -> None:
        db.execute(
            """
            UPDATE sourcing_exchange_rates
            SET exchange_rate = ?, effective_date = CAST(GETDATE() AS DATE)
            WHERE foreign_currency = ?
            """,
            (exchange_rate, foreign_currency)
        )

    # =========================================================================
    # 8. VENDOR MULTI-COMPANY MAPPINGS
    # =========================================================================
    @staticmethod
    def get_vendor_company_mappings(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT m.*, v.vendor_code, v.vendor_name, v.vendor_group, v.currency,
                   c.name AS company_name, c.short_code AS company_code
            FROM sourcing_vendor_company_mappings m
            JOIN sourcing_vendors v ON m.vendor_id = v.id
            JOIN companies c ON m.company_id = c.id
            WHERE COALESCE(v.isDelete, 0) = 0
        """
        params = []
        if company_id:
            sql += " AND m.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY c.short_code, v.vendor_code ASC"
        return db.query(sql, tuple(params) if params else ())
