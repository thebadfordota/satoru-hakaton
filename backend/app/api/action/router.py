from fastapi import APIRouter

action_router = APIRouter(tags=['action'])


@action_router.post('/action/verify')
async def verify_action():
    ...
