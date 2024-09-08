from fastapi.requests import Request
from loguru import logger

DEVICE_ID_KEY = 'device_id'


async def get_device_id(request: Request) -> str:
    logger.info(f'Headers: {request.headers}')
    device_id = request.headers.get(DEVICE_ID_KEY)

    return device_id
