from typing import List, Dict, Any, Optional
from app.core.db import db

class AdminTaxService:
    @staticmethod
    def get_tax_authorities(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT ta.*, c.name AS company_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM admin_tax_profiles tp WHERE tp.authority_id = ta.id) AS profile_count
            FROM admin_tax_authorities ta
            JOIN companies c ON ta.company_id = c.id
        """
        if company_id:
            query += " WHERE ta.company_id = ? ORDER BY ta.code ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY ta.code ASC"
        return db.query(query)

    @staticmethod
    def get_tax_categories() -> List[Dict[str, Any]]:
        return db.query("""
            SELECT tc.*,
                   (SELECT COUNT(*) FROM admin_tax_profiles tp WHERE tp.category_id = tc.id) AS linked_profiles_count
            FROM admin_tax_categories tc
            ORDER BY tc.category_code ASC
        """)

    @staticmethod
    def get_tax_profiles(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT tp.*, c.name AS company_name, c.short_code AS company_code,
                   tc.category_name, tc.category_code, tc.tax_type,
                   ta.authority_name, ta.authority_code
            FROM admin_tax_profiles tp
            JOIN companies c ON tp.company_id = c.id
            JOIN admin_tax_categories tc ON tp.category_id = tc.id
            JOIN admin_tax_authorities ta ON tp.authority_id = ta.id
        """
        if company_id:
            query += " WHERE tp.company_id = ? ORDER BY tp.rate_percent DESC, tp.profile_code ASC"
            return db.query(query, (company_id,))
        query += " ORDER BY tp.rate_percent DESC, tp.profile_code ASC"
        return db.query(query)

    @staticmethod
    def calculate_tax(amount: float, profile_code: str, company_id: Optional[str] = None) -> Dict[str, Any]:
        profiles = AdminTaxService.get_tax_profiles(company_id)
        matched = next((p for p in profiles if p["profile_code"] == profile_code), None)
        if not matched:
            return {"taxable_amount": amount, "tax_rate": 0.0, "tax_amount": 0.0, "total_amount": amount}
        rate = float(matched["rate_percent"])
        tax_amt = round(amount * (rate / 100.0), 2)
        return {
            "profile_code": profile_code,
            "profile_name": matched["profile_name"],
            "tax_type": matched["tax_type"],
            "taxable_amount": amount,
            "tax_rate": rate,
            "tax_amount": tax_amt,
            "total_amount": round(amount + tax_amt, 2),
            "gl_account_code": matched["gl_account_code"]
        }
