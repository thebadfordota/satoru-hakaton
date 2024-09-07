from datetime import datetime
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, CreateUpdateDictModel
from pydantic import Field, EmailStr, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(CreateUpdateDictModel):
    password: str | None = None
    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    position: str | None = None
    task_type: str | None = None
    device_verification_code: str | None = None


class UserCreate(BaseUserCreate):
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = Field(None)
    password: str
    position: str
    task_type: str
