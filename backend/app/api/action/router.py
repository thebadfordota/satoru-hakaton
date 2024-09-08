import asyncio
from io import BytesIO
from typing import Annotated, Any

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from starlette import status

from app import User
from app.api.action.schemas import SimpleResultRequestSchema
from app.api.action.service import send_fcm_message
from app.api.auth.base_config import fastapi_users
from app.api.dependencies import get_device_id
from app.database_config import AsyncSession

import gc
import ctypes
from faster_whisper import WhisperModel

action_router = APIRouter(tags=['action'])

active_user = fastapi_users.current_user(active=True)


async def _get_user_by_device_id(device_id, session) -> User:
    logger.info(device_id)
    stmt = select(User).where(User.device_id == device_id)
    results = await session.execute(stmt)
    user = results.unique().scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    return user


def clear_memory() -> None:
    # torch.cuda.empty_cache()
    gc.collect()
    ctypes.CDLL("libc.so.6").malloc_trim(0)


def transcribe(audio_path: Any,
               model_size: str = 'medium') -> str:  # tiny, base, small, medium, large, large-v2, large-v3
    try:
        model = WhisperModel(model_size, download_root='/models/', local_files_only=False)
        segments, _ = model.transcribe(audio_path)
        return ''.join([segment.text for segment in segments])
    finally:
        clear_memory()


async def wait_result(user, session):
    while True:
        await session.refresh(user)
        if user.task_done is not None and user.task_done:
            return
        elif user.task_done is not None and not user.task_done:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        await asyncio.sleep(1)


@action_router.post('/action/verify')
async def verify_action(user: Annotated[User, Depends(active_user)], session: AsyncSession):
    send_fcm_message()
    timeout_in_seconds = 120
    await asyncio.wait_for(wait_result(user, session), timeout=timeout_in_seconds)


@action_router.post("/action/result/simple")
async def send_simple_result(
    device_id: Annotated[str, Depends(get_device_id)],
    session: AsyncSession,
    request: SimpleResultRequestSchema,
):
    user = await _get_user_by_device_id(device_id, session)
    user.task_done = request.task_done
    await session.commit()
    await session.refresh(user)


@action_router.post("/action/result/file")
async def upload_action_result(
    device_id: Annotated[str, Depends(get_device_id)],
    session: AsyncSession,
    file: UploadFile = File(),
):
    user = await _get_user_by_device_id(device_id, session)
    content = await file.read()
    bts = BytesIO(content)
    message = transcribe(bts).strip('.,!?-:;')
    logger.info(f'Message: {message}')
    if user.expected_result['audio'] == message:
        user.task_done = True
    else:
        user.task_done = False

    await session.commit()
    await session.refresh(user)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "message": message,
    }


@action_router.get("/action/task")
async def get_task(
    device_id: Annotated[str, Depends(get_device_id)],
    session: AsyncSession,
):
    user = await _get_user_by_device_id(device_id, session)
    match user.task_type:
        case 'peach':
            return {
                "task_type": "peach"
            }
        case 'voice':
            return {
                "task_type": "peach",
                "task_content": "Вы должны мне доверять",
            }
        case 'voice':
            return {
                "task_type": "video",
                "task_content": "Приседания",
            }
