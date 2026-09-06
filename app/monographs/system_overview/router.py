from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import psutil
from app.core.templates import templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.manufacturing_ops.service import ManufacturingService
from app.monographs.enterprise_modules.service import EnterpriseModuleService
from app.core.user_service import UserService

router = APIRouter(tags=["System Overview"])

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    companies_list = CompanyService.get_all_companies()
    active_company = CompanyService.resolve_active_company(request, companies=companies_list)
    current_user = UserService.resolve_current_user(request)
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    options = DynamicOptionService.get_options_by_category()
    all_modules = EnterpriseModuleService.get_all_modules()
    grouped_modules = EnterpriseModuleService.get_modules_by_domain(modules=all_modules)
    db_health = db.check_health()
    plant_summary = ManufacturingService.get_plant_summary()
    
    # System host metrics
    cpu_pct = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()

    breadcrumbs = [
        {"title": "Home", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/dashboard.html",
        context={
            "active_company": active_company,
            "current_user": current_user,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "options": options,
            "all_modules": all_modules,
            "grouped_modules": grouped_modules,
            "db_health": db_health,
            "plant_summary": plant_summary,
            "breadcrumbs": breadcrumbs,
            "active_tab": "general",
            "host_metrics": {
                "cpu_percent": cpu_pct,
                "ram_percent": ram.percent,
                "ram_used_gb": round(ram.used / (1024**3), 1),
                "ram_total_gb": round(ram.total / (1024**3), 1)
            }
        }
    )

@router.get("/api/system/metrics", response_class=JSONResponse)
async def get_system_metrics(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    db_health = db.check_health()
    cpu_pct = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    plant_summary = ManufacturingService.get_plant_summary()

    return {
        "active_company": {
            "id": str(active_company["id"]),
            "code": active_company["code"],
            "name": active_company["name"],
            "short_code": active_company["short_code"]
        },
        "db": db_health,
        "cpu_percent": cpu_pct,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 1),
        "ram_total_gb": round(ram.total / (1024**3), 1),
        "plant": plant_summary
    }
