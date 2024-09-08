from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app import User
from app.api.auth.base_config import fastapi_users
from app.api.auth.schemas import UserRead
from app.api.user.schemas import VerificationCodeRequestSchema
from app.database_config import AsyncSession

active_user = fastapi_users.current_user(active=True)
is_superuser = fastapi_users.current_user(superuser=True)

users_router = APIRouter(tags=['users'])


@users_router.get('/users', response_model=list[UserRead], dependencies=[Depends(is_superuser)])
async def get_all_users(session: AsyncSession):
    stmt = select(User)
    result = await session.execute(stmt)
    return result.scalars().all()


@users_router.post('/users/set_verification_code')
async def set_verification_code(
    request: VerificationCodeRequestSchema,
    user: Annotated[User, Depends(active_user)],
    session: AsyncSession,
):
    user.device_verification_code = request.device_verification_code
    await session.commit()
    await session.refresh(user)
