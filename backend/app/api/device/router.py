from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app import User
from app.api.device.schemas import ActivateDeviceResponseSchema
from app.api.user.schemas import VerificationCodeRequestSchema
from app.database_config import AsyncSession

device_router = APIRouter(tags=['device'])


@device_router.post('/device/activate', response_model=ActivateDeviceResponseSchema)
async def activate_device(request: VerificationCodeRequestSchema, session: AsyncSession):
    stmt = select(User).where(User.device_verification_code == request.device_verification_code)
    results = await session.execute(stmt)
    user = results.unique().scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    device_id = uuid4()
    user.device_id = str(device_id)
    user.device_verification_code = None

    await session.commit()
    await session.refresh(user)
    return ActivateDeviceResponseSchema(device_id=device_id)
