from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.manufacturing_ops.service import ManufacturingService

router = APIRouter(tags=["Manufacturing Operations"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/settings/manufacturing", response_class=HTMLResponse)
async def manufacturing_page(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    machines = ManufacturingService.get_all_machines()
    plant_summary = ManufacturingService.get_plant_summary()
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Plant Operations", "url": "/"},
        {"title": "Line Telemetry", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/manufacturing.html",
        context={
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "machines": machines,
            "plant_summary": plant_summary,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "manufacturing"
        }
    )

@router.post("/api/manufacturing/machine-status", response_class=JSONResponse)
async def change_machine_status(
    request: Request,
    machine_code: str = Form(...),
    status: str = Form(...)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = ManufacturingService.update_machine_status(
        machine_code=machine_code,
        new_status=status,
        user="Operator Admin",
        ip=client_ip
    )
    return {"success": success, "machine_code": machine_code, "new_status": status}

@router.post("/api/manufacturing/line-speed", response_class=JSONResponse)
async def change_line_speed(
    request: Request,
    machine_code: str = Form(...),
    speed: int = Form(...)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = ManufacturingService.adjust_line_speed(
        machine_code=machine_code,
        new_speed=speed,
        user="Operator Admin",
        ip=client_ip
    )
    return {"success": success, "machine_code": machine_code, "new_speed": speed}
