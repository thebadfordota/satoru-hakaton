from fastapi import APIRouter

action_router = APIRouter(tags=['Action methods'])


@action_router.post('/action/verify')
async def verify_action():
    ...
