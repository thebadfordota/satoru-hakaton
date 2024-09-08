from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends
from loguru import logger

from app.api.dependencies import get_device_id

action_router = APIRouter(tags=['action'])


@action_router.post('/action/verify')
async def verify_action():
    ...


# @action_router.post("/action/result/file")
# async def upload_action_result(file: UploadFile = File()):
#     content = await file.read()
#     return {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "size": len(content),
#     }


@action_router.post("/action/result/file")
async def upload_action_result(device_id: Annotated[str, Depends(get_device_id)], file: UploadFile = File()):
    logger.info(device_id)
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }
