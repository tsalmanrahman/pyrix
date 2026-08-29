from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.sql_inspector.service import SQLInspectorService

router = APIRouter(tags=["SQL Inspector"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/settings/database", response_class=HTMLResponse)
async def sql_inspector_page(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    db_overview = SQLInspectorService.get_server_overview()
    tables_info = SQLInspectorService.get_tables_info()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "System Administration", "url": "/"},
        {"title": "SQL Server Diagnostics", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/sql_inspector.html",
        context={
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "db_overview": db_overview,
            "tables_info": tables_info,
            "db_health": db_overview,
            "breadcrumbs": breadcrumbs,
            "active_tab": "database"
        }
    )

@router.post("/api/sql/execute", response_class=JSONResponse)
async def execute_query(
    sql_query: str = Form(...)
):
    result = SQLInspectorService.execute_custom_query(sql_query)
    return result
