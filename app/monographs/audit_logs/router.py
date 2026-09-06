from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from app.core.templates import templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.audit_logs.service import AuditService

router = APIRouter(tags=["Security & Audit"])

@router.get("/settings/security", response_class=HTMLResponse)
async def security_page(request: Request, action: Optional[str] = None):
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    logs = AuditService.get_logs(limit=100, action_filter=action)
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Security & Governance", "url": "/"},
        {"title": "Audit Logs & Security", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/audit_logs.html",
        context={
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "logs": logs,
            "selected_action": action,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "security"
        }
    )

@router.post("/api/audit/clear", response_class=JSONResponse)
async def clear_audit_logs():
    AuditService.clear_logs()
    return {"success": True, "message": "Audit logs cleared."}
