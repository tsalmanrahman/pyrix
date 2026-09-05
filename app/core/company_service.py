from typing import List, Dict, Any, Optional
from fastapi import Request
from app.core.db import db
from app.core.cache import cache

COMPANY_EMOJI_MAP = {
    "APEX": "🏭",
    "HORIZON": "🏢",
    "DELTA": "🚢",
    "TITAN": "⚙️",
    "PRIME": "🛍️",
}

class CompanyService:
    COOKIE_NAME = "pyrix_active_company_id"

    @staticmethod
    def _enrich(comp: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not comp:
            return None
        code = comp.get("short_code", "")
        comp["logo_emoji"] = COMPANY_EMOJI_MAP.get(code, "🏢")
        return comp

    @staticmethod
    def get_all_companies() -> List[Dict[str, Any]]:
        cached = cache.get("all_companies")
        if cached:
            return cached
        try:
            companies = db.query(
                "SELECT * FROM companies WHERE is_active = 1 ORDER BY sort_order ASC, code ASC"
            )
            if companies:
                enriched = [CompanyService._enrich(c) for c in companies]
                cache.set("all_companies", enriched, ttl=300.0)
                return enriched
        except Exception:
            pass
        return [CompanyService.get_default_company()]

    @staticmethod
    def get_company_by_id(company_id: str) -> Optional[Dict[str, Any]]:
        companies = CompanyService.get_all_companies()
        for comp in companies:
            if str(comp.get("id")) == str(company_id):
                return comp
        return CompanyService.get_default_company()

    @staticmethod
    def get_company_by_code(code: int) -> Optional[Dict[str, Any]]:
        try:
            comp = db.query_one(
                "SELECT * FROM companies WHERE code = ?",
                (code,)
            )
            return CompanyService._enrich(comp)
        except Exception:
            return CompanyService.get_default_company()

    @staticmethod
    def get_default_company() -> Dict[str, Any]:
        try:
            company = db.query_one(
                "SELECT TOP 1 * FROM companies WHERE is_active = 1 ORDER BY sort_order ASC, code ASC"
            )
        except Exception:
            company = None
        if not company:
            return {
                "id": "00000000-0000-0000-0000-000000000000",
                "code": 101,
                "name": "Apex Precision Manufacturing Group Ltd",
                "short_code": "APEX",
                "logo_emoji": "🏭",
                "industry": "Precision Heavy Manufacturing",
                "tagline": "Industrial Automation & SMT Microelectronics",
                "currency": "USD",
                "fiscal_year": "FY 2026-2027",
                "headquarters": "Plant Delta 01 - Industrial Park",
                "logo_icon": "factory",
                "accent_color": "#2563EB"
            }
        return CompanyService._enrich(company)

    @staticmethod
    def resolve_active_company(request: Request, companies: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Resolves the currently selected company from session cookies or falls back to default."""
        cookie_id = request.cookies.get(CompanyService.COOKIE_NAME)
        company_list = companies if companies is not None else CompanyService.get_all_companies()
        if cookie_id and company_list:
            for comp in company_list:
                if str(comp.get("id")) == str(cookie_id):
                    return comp
        return company_list[0] if company_list else CompanyService.get_default_company()
