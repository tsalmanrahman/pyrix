from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.templates import templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.core.user_service import UserService

router = APIRouter(tags=["Appearance"])

@router.get("/settings/appearance", response_class=HTMLResponse)
async def appearance_page(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    current_user = UserService.resolve_current_user(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "System Settings", "url": "/"},
        {"title": "Appearance", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/appearance.html",
        context={
            "active_company": active_company,
            "current_user": current_user,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "appearance"
        }
    )

@router.post("/api/appearance/update", response_class=JSONResponse)
async def update_appearance(
    request: Request,
    theme_mode: str = Form(...),
    accent_color: str = Form(...),
    glass_blur_px: int = Form(...),
    glass_opacity_pct: int = Form(...),
    sidebar_style: str = Form(...),
    border_glow: int = Form(1)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = AppearanceService.update_appearance(
        theme_mode=theme_mode,
        accent_color=accent_color,
        glass_blur_px=glass_blur_px,
        glass_opacity_pct=glass_opacity_pct,
        sidebar_style=sidebar_style,
        border_glow=border_glow,
        user="Operator Admin",
        ip=client_ip
    )
    return {"success": success, "message": "Appearance settings updated successfully."}
