from fastapi import HTTPException
from fastapi.requests import Request
from loguru import logger

DEVICE_ID_KEY = 'DEVICE_ID'


async def get_device_id(request: Request) -> str:
    logger.info(f'Headers: {request.headers}')
    device_id = request.headers.get(DEVICE_ID_KEY)

    if device_id is None:
        raise HTTPException(status_code=401)

    return device_id
