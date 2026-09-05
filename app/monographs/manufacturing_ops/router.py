from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.core.templates import templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.manufacturing_ops.service import ManufacturingService

router = APIRouter(tags=["Manufacturing Operations"])

@router.get("/settings/manufacturing")
async def manufacturing_page(request: Request):
    # Consolidated with Enterprise Production Operations Suite
    return RedirectResponse(url="/modules/production?tab=resources", status_code=307)

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
