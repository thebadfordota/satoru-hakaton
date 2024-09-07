from fastapi import APIRouter

from app.api.action.router import action_router
from app.api.auth.base_config import auth_backend, fastapi_users
from app.api.auth.schemas import UserRead, UserCreate, UserUpdate
from app.api.device.router import device_router

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

router.include_router(action_router)
router.include_router(device_router)
