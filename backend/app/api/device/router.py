from fastapi import APIRouter

device_router = APIRouter(tags=['Device methods'])


@device_router.post('/device/activate')
async def activate_device():
    ...
