from fastapi import HTTPException
from fastapi.requests import Request
from loguru import logger

DEVICE_ID_KEY = 'device_id'


async def get_device_id(request: Request) -> str:
    logger.info(f'Headers: {request.headers}')
    device_id = request.headers.get(DEVICE_ID_KEY)

    if device_id is None:
        device_id = '21afb99f-197d-40cb-bef0-b479f9eb974d'

    return device_id
