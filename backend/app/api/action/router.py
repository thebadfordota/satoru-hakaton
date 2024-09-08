from io import BytesIO
from typing import Annotated, Any

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from starlette import status

from app import User
from app.api.action.schemas import SimpleResultRequestSchema
from app.api.dependencies import get_device_id
from app.database_config import AsyncSession

import gc
import ctypes
from faster_whisper import WhisperModel

# import torch

action_router = APIRouter(tags=['action'])


@action_router.post('/action/verify')
async def verify_action():
    ...


# @action_router.post("/action/result/simple")
# async def upload_action_result(
#     device_id: Annotated[str, Depends(get_device_id)],
#     session: AsyncSession,
#     request: SimpleResultRequestSchema
# ):
#     stmt = select(User).where(User.device_id == device_id)
#     results = await session.execute(stmt)
#     user = results.unique().scalar_one_or_none()
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
#
#     user.device_id = str(device_id)
#     user.device_verification_code = None
#
#     await session.commit()
#     await session.refresh(user)
#     return ActivateDeviceResponseSchema(device_id=device_id)


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


@action_router.post("/action/result/file")
async def upload_action_result(device_id: Annotated[str, Depends(get_device_id)], file: UploadFile = File()):
    logger.info(device_id)
    content = await file.read()
    bts = BytesIO(content)
    message = transcribe(bts)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "message": message,
    }


@action_router.post("/action/result/test_video_content")
async def test_video_content(device_id: Annotated[str, Depends(get_device_id)], file: UploadFile = File()):
    logger.info(device_id)
    content = await file.read()
    bts = BytesIO(content)
    # .....
    output = None
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "output": output,
    }
