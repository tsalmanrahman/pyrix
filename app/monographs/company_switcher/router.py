from fastapi import APIRouter, Request, Response, Form
from fastapi.responses import JSONResponse, RedirectResponse
from app.core.company_service import CompanyService

router = APIRouter(tags=["Company Switcher"])

@router.get("/companies")
async def redirect_companies_to_home():
    return RedirectResponse(url="/", status_code=303)

@router.get("/api/companies/list", response_class=JSONResponse)
async def list_companies():
    companies = CompanyService.get_all_companies()
    return {"companies": companies}

@router.post("/api/company/switch")
async def switch_company(
    request: Request,
    response: Response,
    company_id: str = Form(...),
    redirect_to: str = Form(None)
):
    comp = CompanyService.get_company_by_id(company_id)
    if not comp:
        return JSONResponse(status_code=404, content={"success": False, "error": "Company not found"})

    # If form submission requests a redirect
    if redirect_to or "text/html" in request.headers.get("accept", ""):
        target_url = redirect_to if redirect_to else "/"
        red = RedirectResponse(url=target_url, status_code=303)
        red.set_cookie(
            key="pyrix_active_company_id",
            value=str(comp["id"]),
            max_age=30 * 24 * 3600,
            httponly=False,
            samesite="lax"
        )
        return red

    # Return JSON for modal
    res = JSONResponse(content={
        "success": True,
        "company": {
            "id": str(comp["id"]),
            "code": comp["code"],
            "name": comp["name"],
            "short_code": comp["short_code"],
            "industry": comp["industry"],
            "fiscal_year": comp["fiscal_year"]
        }
    })
    res.set_cookie(
        key="pyrix_active_company_id",
        value=str(comp["id"]),
        max_age=30 * 24 * 3600,
        httponly=False,
        samesite="lax"
    )
    return res
