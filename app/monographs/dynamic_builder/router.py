from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from app.core.templates import templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.core.user_service import UserService

router = APIRouter(tags=["Dynamic Builder"])

class ReorderRequest(BaseModel):
    order: List[int]

@router.get("/settings/dynamic-options", response_class=HTMLResponse)
async def dynamic_options_page(request: Request, category: Optional[str] = None):
    active_company = CompanyService.resolve_active_company(request)
    current_user = UserService.resolve_current_user(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    options = DynamicOptionService.get_options_by_category(category)
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "System Administration", "url": "/"},
        {"title": "Dynamic Layout & Field Studio", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/dynamic_options.html",
        context={
            "active_company": active_company,
            "current_user": current_user,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "options": options,
            "selected_category": category,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "dynamic_fields"
        }
    )

@router.post("/api/dynamic-options/update-value", response_class=JSONResponse)
async def update_option_value(
    request: Request,
    option_key: str = Form(...),
    value: str = Form(...)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = DynamicOptionService.update_option_value(
        option_key=option_key,
        new_value=value,
        user="Operator Admin",
        ip=client_ip
    )
    return {"success": success, "option_key": option_key, "value": value}

@router.post("/api/dynamic-options/reorder", response_class=JSONResponse)
async def reorder_dynamic_options(
    request: Request,
    payload: ReorderRequest = Body(...)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = DynamicOptionService.reorder_options(
        order_list=payload.order,
        user="Operator Admin",
        ip=client_ip
    )
    return {"success": success, "message": "Layout reordered successfully."}

@router.post("/api/dynamic-options/create", response_class=JSONResponse)
async def create_custom_option(
    request: Request,
    option_key: str = Form(...),
    category_code: str = Form(...),
    label: str = Form(...),
    description: str = Form(""),
    field_type: str = Form(...),
    default_value: str = Form(""),
    unit: Optional[str] = Form(None),
    icon: str = Form("sliders"),
    min_val: Optional[float] = Form(None),
    max_val: Optional[float] = Form(None),
    step_val: Optional[float] = Form(None),
    options_json: Optional[str] = Form(None)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    active_company = CompanyService.resolve_active_company(request)
    try:
        success = DynamicOptionService.create_custom_option(
            company_id=str(active_company["id"]),
            option_key=option_key,
            category_code=category_code,
            label=label,
            description=description,
            field_type=field_type,
            default_value=default_value,
            unit=unit,
            icon=icon,
            min_val=min_val,
            max_val=max_val,
            step_val=step_val,
            options_json=options_json,
            user="Operator Admin",
            ip=client_ip
        )
        return {"success": success, "message": "Dynamic field created successfully."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/dynamic-options/delete", response_class=JSONResponse)
async def delete_custom_option(
    request: Request,
    option_key: str = Form(...)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = DynamicOptionService.delete_custom_option(
        option_key=option_key,
        user="Operator Admin",
        ip=client_ip
    )
    if not success:
        return {"success": False, "error": "Cannot delete system protected fields."}
    return {"success": True, "message": "Field deleted successfully."}
