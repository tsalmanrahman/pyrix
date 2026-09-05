import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from app.config import get_settings
from app.core.init_db import setup_database
from app.core.user_service import UserService

# Import Monograph Routers
from app.monographs.system_overview.router import router as system_router
from app.monographs.appearance.router import router as appearance_router
from app.monographs.dynamic_builder.router import router as dynamic_builder_router
from app.monographs.sql_inspector.router import router as sql_inspector_router
from app.monographs.manufacturing_ops.router import router as manufacturing_router
from app.monographs.audit_logs.router import router as audit_router
from app.monographs.enterprise_modules.router import router as enterprise_modules_router
from app.monographs.company_switcher.router import router as company_switcher_router
from app.monographs.auth.router import router as auth_router
from app.core.dynamic_crud_router import crud_router

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Pyrix-Main")

class SessionInactivityMiddleware(BaseHTTPMiddleware):
    """Guards all application routes, requiring login and enforcing 2-hour inactivity timeout."""
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Whitelisted public paths
        if (
            path.startswith("/static")
            or path.startswith("/login")
            or path == "/favicon.ico"
            or path == "/api/health"
        ):
            return await call_next(request)
        
        user_id = request.cookies.get(UserService.COOKIE_USER_ID)
        
        # 1. Enforce authentication
        if not user_id:
            if path.startswith("/api/"):
                return JSONResponse(status_code=401, content={"success": False, "error": "Authentication required. Please sign in."})
            return RedirectResponse(url=f"/login?next_url={path}", status_code=303)
        
        # 2. Enforce 1-Hour Inactivity Timeout (3600 seconds)
        last_act_str = request.cookies.get("pyrix_last_activity")
        now_ts = int(time.time())
        if last_act_str:
            try:
                last_act = int(last_act_str)
                if (now_ts - last_act) > 3600:
                    if path.startswith("/api/"):
                        res = JSONResponse(status_code=401, content={"success": False, "error": "Session expired due to 1 hour of inactivity."})
                    else:
                        res = RedirectResponse(url="/login?error=Your+session+has+expired+due+to+1+hour+of+inactivity.+Please+sign+in+again.", status_code=303)
                    res.delete_cookie(UserService.COOKIE_USER_ID)
                    res.delete_cookie(UserService.COOKIE_SESSION)
                    res.delete_cookie("pyrix_last_activity")
                    return res
            except ValueError:
                pass

        response = await call_next(request)
        
        # 3. Refresh activity timestamp on successful response
        if not path.startswith("/logout"):
            response.set_cookie(
                key="pyrix_last_activity",
                value=str(now_ts),
                httponly=True,
                samesite="lax"
            )
        
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Pyrix Engine & MS SQL Server 2025 tables with GUID/INT standards...")
    try:
        setup_database()
        logger.info("PyrixDB initialized and ready.")
    except Exception as e:
        logger.error(f"Database startup error: {e}")
    yield
    logger.info("Pyrix Engine shutting down cleanly.")

app = FastAPI(
    title="Pyrix — Multi-Company Operations & Settings Suite",
    description="Enterprise hybrid macOS & Windows 11 Modern Settings application backed by Microsoft SQL Server 2025.",
    version="3.0.0",
    lifespan=lifespan
)

# Register Session Inactivity & Auth Guard Middleware
app.add_middleware(SessionInactivityMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register Feature Monograph Routers
app.include_router(system_router)
app.include_router(appearance_router)
app.include_router(dynamic_builder_router)
app.include_router(sql_inspector_router)
app.include_router(manufacturing_router)
app.include_router(audit_router)
app.include_router(enterprise_modules_router)
app.include_router(company_switcher_router)
app.include_router(auth_router)
app.include_router(crud_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error on {request.url.path}: {exc}")
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(exc)}
        )
    raise exc

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
