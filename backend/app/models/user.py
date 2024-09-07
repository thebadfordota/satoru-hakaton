from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .sqlalchemy_model import SqlAlchemyModel


class User(SQLAlchemyBaseUserTableUUID, SqlAlchemyModel):
    """Модель пользователя"""

    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(
        String(length=32),
        nullable=False,
        unique=True,
        comment='Электронная почта'
    )
    username: Mapped[str] = mapped_column(String(length=32), nullable=False, comment='Имя пользователя')
    first_name: Mapped[str] = mapped_column(String(length=32), nullable=False, comment='Имя')
    last_name: Mapped[str] = mapped_column(String(length=32), nullable=False, comment='Фамилия')
    patronymic: Mapped[str] = mapped_column(String(length=32), nullable=True, comment='Отчество')
    position: Mapped[str] = mapped_column(String(length=256), nullable=False, comment='Должность')
    task_type: Mapped[str] = mapped_column(String(length=32), nullable=False, comment='Тип задачи')
    device_verification_code: Mapped[str] = mapped_column(
        String(length=10),
        nullable=True,
        comment='Код подтверждения для устройства'
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment='Дата регистрации'
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=256),
        nullable=False,
        comment='Хэшированный пароль'
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment='Активен?'
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment='Суперпользователь?'
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment='Верифицирован?'
    )