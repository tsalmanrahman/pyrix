from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid

from app.core.company_service import CompanyService
from app.core.user_service import UserService
from app.monographs.appearance.service import AppearanceService

import time

router = APIRouter(tags=["Authentication & User Profile"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    error: Optional[str] = None,
    next_url: Optional[str] = "/"
):
    current_user = UserService.resolve_current_user(request)
    if current_user:
        return RedirectResponse(url=next_url if next_url and next_url != "/login" else "/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="pages/login.html",
        context={
            "error": error,
            "next_url": next_url or "/"
        }
    )

@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next_url: Optional[str] = Form("/"),
    remember: Optional[str] = Form(None)
):
    user = UserService.authenticate(email, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={
                "error": "Invalid Username or Password. Please try again.",
                "next_url": next_url or "/"
            },
            status_code=401
        )

    accessible_companies = UserService.get_accessible_companies(user)
    now_ts = int(time.time())

    primary_company_id = user.get("primary_company_id")
    target_company = None
    if primary_company_id:
        target_company = CompanyService.get_company_by_id(str(primary_company_id))

    # Dynamic Routing:
    # 1. If operating company is defined on user profile, log in directly and bind session
    # 2. If user only has 1 accessible company, bind and log in directly
    # 3. Otherwise (no primary company defined AND multiple accessible companies), show /select-company picker
    if target_company:
        redirect_target = next_url if next_url and next_url not in ("/login", "/select-company") else "/"
        active_company_id_to_set = str(target_company["id"])
    elif len(accessible_companies) == 1:
        redirect_target = next_url if next_url and next_url not in ("/login", "/select-company") else "/"
        active_company_id_to_set = str(accessible_companies[0]["id"])
    else:
        redirect_target = f"/select-company?next_url={next_url or '/'}"
        active_company_id_to_set = None

    response = RedirectResponse(url=redirect_target, status_code=303)

    max_age = 60 * 60 * 24 * 30 if remember else None
    response.set_cookie(
        key=UserService.COOKIE_USER_ID,
        value=str(user["id"]),
        max_age=max_age,
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key=UserService.COOKIE_SESSION,
        value=str(uuid.uuid4()),
        max_age=max_age,
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key="pyrix_last_activity",
        value=str(now_ts),
        max_age=max_age,
        httponly=True,
        samesite="lax"
    )

    if active_company_id_to_set:
        response.set_cookie(
            key=CompanyService.COOKIE_NAME,
            value=active_company_id_to_set,
            max_age=max_age,
            httponly=False,
            samesite="lax"
        )

    user_theme = user.get("theme_pref") or "light"
    response.set_cookie(
        key="pyrix_theme",
        value=user_theme,
        max_age=60 * 60 * 24 * 365,
        httponly=False,
        samesite="lax"
    )

    return response

@router.get("/select-company", response_class=HTMLResponse)
async def select_company_page(request: Request, next_url: Optional[str] = "/"):
    current_user = UserService.resolve_current_user(request)
    if not current_user:
        return RedirectResponse(url=f"/login?next_url=/select-company", status_code=303)

    accessible_companies = UserService.get_accessible_companies(current_user)
    if len(accessible_companies) == 1:
        res = RedirectResponse(url=next_url if next_url and next_url not in ("/login", "/select-company") else "/", status_code=303)
        res.set_cookie(
            key=CompanyService.COOKIE_NAME,
            value=str(accessible_companies[0]["id"]),
            httponly=False,
            samesite="lax"
        )
        return res

    return templates.TemplateResponse(
        request=request,
        name="pages/select_company.html",
        context={
            "current_user": current_user,
            "companies": accessible_companies,
            "next_url": next_url or "/"
        }
    )

@router.post("/select-company")
async def select_company_submit(
    request: Request,
    company_id: str = Form(...),
    next_url: Optional[str] = Form("/")
):
    current_user = UserService.resolve_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    comp = CompanyService.get_company_by_id(company_id)
    target = next_url if next_url and next_url not in ("/login", "/select-company") else "/"
    response = RedirectResponse(url=target, status_code=303)
    if comp:
        response.set_cookie(
            key=CompanyService.COOKIE_NAME,
            value=str(comp["id"]),
            httponly=False,
            samesite="lax"
        )
    return response

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(UserService.COOKIE_USER_ID)
    response.delete_cookie(UserService.COOKIE_SESSION)
    response.delete_cookie("pyrix_last_activity")
    response.set_cookie(
        key="pyrix_theme",
        value="light",
        max_age=31536000,
        httponly=False,
        samesite="lax"
    )
    return response

@router.post("/api/user/theme-pref")
async def set_user_theme_pref(request: Request):
    """Dynamically saves the user's selected theme preference in SQL Server."""
    current_user = UserService.resolve_current_user(request)
    selected_theme = "light"
    
    # Try parsing JSON or Form data
    try:
        data = await request.json()
        if isinstance(data, dict) and "theme_pref" in data:
            selected_theme = data["theme_pref"]
    except Exception:
        form = await request.form()
        if "theme_pref" in form:
            selected_theme = form["theme_pref"]

    selected_theme = "dark" if str(selected_theme).strip().lower() == "dark" else "light"

    if current_user and "id" in current_user:
        UserService.update_theme_pref(str(current_user["id"]), selected_theme)

    from fastapi.responses import JSONResponse
    response = JSONResponse({"success": True, "theme_pref": selected_theme})
    response.set_cookie(
        key="pyrix_theme",
        value=selected_theme,
        max_age=60 * 60 * 24 * 365,
        httponly=False,
        samesite="lax"
    )
    return response

@router.get("/profile", response_class=HTMLResponse)
async def user_profile_page(request: Request, success_msg: Optional[str] = None):
    current_user = UserService.resolve_current_user(request)
    active_company = CompanyService.resolve_active_company(request)
    companies = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Settings", "url": "/settings/dynamic-options"},
        {"title": "My Profile & Account", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/user_profile.html",
        context={
            "user": current_user,
            "current_user": current_user,
            "active_company": active_company,
            "companies": companies,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "profile",
            "success_msg": success_msg
        }
    )

@router.post("/profile", response_class=HTMLResponse)
async def update_user_profile(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(""),
    job_title: str = Form(...),
    department: str = Form(...),
    primary_company_id: Optional[str] = Form(None)
):
    current_user = UserService.resolve_current_user(request)
    cleaned_company_id = primary_company_id.strip() if primary_company_id and str(primary_company_id).strip() else None

    UserService.update_profile(
        user_id=str(current_user["id"]),
        full_name=full_name,
        email=email,
        phone=phone or "",
        job_title=job_title,
        department=department,
        primary_company_id=cleaned_company_id
    )

    # Re-fetch updated user
    updated_user = UserService.get_user_by_id(str(current_user["id"]))
    active_company = CompanyService.resolve_active_company(request)
    companies = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Settings", "url": "/settings/dynamic-options"},
        {"title": "My Profile & Account", "url": None}
    ]

    response = templates.TemplateResponse(
        request=request,
        name="pages/user_profile.html",
        context={
            "user": updated_user,
            "current_user": updated_user,
            "active_company": active_company,
            "companies": companies,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "profile",
            "success_msg": "Profile information updated successfully."
        }
    )

    # If operating company was set, sync active company cookie
    if cleaned_company_id:
        response.set_cookie(
            key=CompanyService.COOKIE_NAME,
            value=cleaned_company_id,
            httponly=False,
            samesite="lax"
        )

    return response

@router.post("/profile/change-password", response_class=HTMLResponse)
async def change_user_password(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    current_user = UserService.resolve_current_user(request)
    active_company = CompanyService.resolve_active_company(request)
    companies = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Settings", "url": "/settings/dynamic-options"},
        {"title": "My Profile & Account", "url": None}
    ]

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="pages/user_profile.html",
            context={
                "user": current_user,
                "current_user": current_user,
                "active_company": active_company,
                "companies": companies,
                "appearance": appearance,
                "breadcrumbs": breadcrumbs,
                "active_tab": "profile",
                "error_msg": "Passwords do not match. Please verify and try again."
            }
        )

    UserService.change_password(str(current_user["id"]), new_password)

    return templates.TemplateResponse(
        request=request,
        name="pages/user_profile.html",
        context={
            "user": current_user,
            "current_user": current_user,
            "active_company": active_company,
            "companies": companies,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "profile",
            "success_msg": "Password updated successfully."
        }
    )
