from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from app.core.dynamic_crud_service import DynamicCrudService
from app.core.user_service import UserService

crud_router = APIRouter(prefix="/api/crud", tags=["Universal Dynamic CRUD"])

@crud_router.get("/{entity}/{record_id}")
async def get_record(entity: str, record_id: str):
    data = DynamicCrudService.get_record(entity, record_id)
    if not data:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "payload": data}

@crud_router.post("/{entity}/{record_id}/update")
async def update_record(entity: str, record_id: str, request: Request):
    user = request.cookies.get(UserService.COOKIE_USER_ID, "System Admin")
    form_data = await request.json()
    result = DynamicCrudService.update_record(entity, record_id, form_data, user=user)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
    return result

@crud_router.get("/{entity}/{record_id}/precheck-delete")
async def precheck_delete(entity: str, record_id: str):
    return DynamicCrudService.check_dependencies(entity, record_id)

@crud_router.post("/{entity}/{record_id}/delete")
async def delete_record(entity: str, record_id: str, request: Request):
    user = request.cookies.get(UserService.COOKIE_USER_ID, "System Admin")
    result = DynamicCrudService.delete_record(entity, record_id, user=user)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deletion failed"))
    return result
