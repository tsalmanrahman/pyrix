from typing import List, Dict, Any, Optional
from app.core.db import db

class AdminMasterService:
    @staticmethod
    def get_companies(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT c.*,
                   cfg.registration_no, cfg.tax_id, cfg.base_currency, cfg.fiscal_start_month,
                   cfg.multi_currency_enabled, cfg.address_line1, cfg.city, cfg.state,
                   cfg.postal_code, cfg.country, cfg.phone, cfg.email, cfg.website,
                   cfg.default_locale, cfg.status AS config_status,
                   (SELECT COUNT(*) FROM admin_business_units bu WHERE bu.company_id = c.id) AS bu_count,
                   (SELECT COUNT(*) FROM admin_cost_centers cc WHERE cc.company_id = c.id) AS cc_count,
                   (SELECT COUNT(*) FROM admin_user_profiles usr WHERE usr.company_id = c.id) AS user_count
            FROM companies c
            LEFT JOIN admin_company_configs cfg ON c.id = cfg.company_id
        """
        if company_id:
            query += " WHERE c.id = ? ORDER BY c.sort_order ASC, c.name ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY c.sort_order ASC, c.name ASC"
        return db.query(query)

    @staticmethod
    def get_business_units(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT bu.*, c.name AS company_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM admin_cost_centers cc WHERE cc.business_unit_id = bu.id) AS cc_count
            FROM admin_business_units bu
            JOIN companies c ON bu.company_id = c.id
        """
        if company_id:
            query += " WHERE bu.company_id = ? ORDER BY bu.code ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY bu.code ASC"
        return db.query(query)

    @staticmethod
    def get_cost_centers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT cc.*, c.name AS company_name, c.short_code AS company_code,
                   bu.unit_name, bu.unit_code
            FROM admin_cost_centers cc
            JOIN companies c ON cc.company_id = c.id
            JOIN admin_business_units bu ON cc.business_unit_id = bu.id
        """
        if company_id:
            query += " WHERE cc.company_id = ? ORDER BY cc.code ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY cc.code ASC"
        return db.query(query)

    @staticmethod
    def get_countries() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM admin_countries ORDER BY country_name ASC")

    @staticmethod
    def get_states(country_code: Optional[str] = None) -> List[Dict[str, Any]]:
        if country_code:
            return db.query("SELECT * FROM admin_states WHERE country_code = ? ORDER BY state_name ASC", (country_code,))
        return db.query("SELECT * FROM admin_states ORDER BY country_code ASC, state_name ASC")

    @staticmethod
    def get_currencies() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM admin_currencies ORDER BY is_base_currency DESC, currency_code ASC")

    @staticmethod
    def get_exchange_rates(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT xr.*, c.name AS company_name, c.short_code AS company_code,
                   cur.currency_name, cur.symbol
            FROM admin_exchange_rates xr
            JOIN companies c ON xr.company_id = c.id
            LEFT JOIN admin_currencies cur ON xr.currency_code = cur.currency_code
        """
        if company_id:
            query += " WHERE xr.company_id = ? ORDER BY xr.effective_date DESC, xr.currency_code ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY xr.effective_date DESC, xr.currency_code ASC"
        return db.query(query)

    @staticmethod
    def get_fiscal_calendars(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT fc.*, c.name AS company_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM admin_fiscal_periods fp WHERE fp.calendar_id = fc.id) AS period_count,
                   (SELECT COUNT(*) FROM admin_fiscal_periods fp WHERE fp.calendar_id = fc.id AND fp.status = 'HARD_CLOSED') AS closed_periods
            FROM admin_fiscal_calendars fc
            JOIN companies c ON fc.company_id = c.id
        """
        if company_id:
            query += " WHERE fc.company_id = ? ORDER BY fc.start_date DESC"
            return db.query(query, (company_id,))
        query += " ORDER BY fc.start_date DESC"
        return db.query(query)

    @staticmethod
    def get_fiscal_periods(company_id: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT fp.*, fc.fiscal_year_name, fc.company_id, c.name AS company_name, c.short_code AS company_code
            FROM admin_fiscal_periods fp
            JOIN admin_fiscal_calendars fc ON fp.calendar_id = fc.id
            JOIN companies c ON fc.company_id = c.id
            WHERE 1=1
        """
        params = []
        if calendar_id:
            query += " AND fp.calendar_id = ?"
            params.append(calendar_id)
        elif company_id:
            query += " AND fc.company_id = ?"
            params.append(company_id)
        query += " ORDER BY fp.period_number ASC"
        return db.query(query, tuple(params)) if params else db.query(query)

    @staticmethod
    def get_printers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT p.*, c.name AS company_name, c.short_code AS company_code
            FROM admin_printers p
            JOIN companies c ON p.company_id = c.id
        """
        if company_id:
            query += " WHERE p.company_id = ? ORDER BY p.is_default DESC, p.printer_name ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY p.is_default DESC, p.printer_name ASC"
        return db.query(query)
