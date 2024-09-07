from datetime import datetime
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import Field


class UserRead(BaseUser[UUID]):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None
    position: str
    task_type: str
    registered_at: datetime
    device_verification_code: str | None


class UserUpdate(BaseUserUpdate):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None
    position: str
    task_type: str
    registered_at: datetime
    device_verification_code: str | None = Field(None)


class UserCreate(BaseUserCreate):
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = Field(None)
    password: str
    position: str
    task_type: str
