from fastapi import APIRouter, Depends

from app.api.action.router import action_router
from app.api.auth.base_config import auth_backend, fastapi_users
from app.api.auth.schemas import UserRead, UserCreate, UserUpdate
from app.api.device.router import device_router
from app.api.user.router import users_router

is_superuser = fastapi_users.current_user(superuser=True)

router = APIRouter(
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    dependencies=[Depends(is_superuser)],
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    dependencies=[Depends(is_superuser)],
    prefix="/users",
    tags=["users"],
)

router.include_router(action_router)
router.include_router(device_router)
router.include_router(users_router)
