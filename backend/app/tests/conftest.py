from typing import AsyncGenerator, Generator

import psycopg2
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pydantic import PostgresDsn
from pytest_alembic import Config, runner
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, create_async_engine
from sqlalchemy.orm import close_all_sessions

from app.database_config import get_session
from main import app
from settings import settings


@pytest.fixture
def base_url() -> str:
    return f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def async_db_engine() -> AsyncEngine:
    """Create async database engine and dispose it after all tests.

    Yields:
        async_engine (AsyncEngine): SQLAlchemy AsyncEngine instance.
    """
    async_engine = create_async_engine(url=settings.DB_URI, echo=settings.ECHO_SQL)
    try:
        yield async_engine
    finally:
        close_all_sessions()
        await async_engine.dispose()


@pytest.mark.asyncio
@pytest.fixture
async def session_factory(async_db_engine: AsyncEngine) -> async_sessionmaker:
    """Create async session factory."""
    return async_sessionmaker(bind=async_db_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.mark.asyncio
@pytest.fixture()
async def async_db_session(session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for database and rollback it after test."""
    async with session_factory() as async_session:
        try:
            yield async_session
        finally:
            await async_session.rollback()
            await async_session.close()


@pytest.fixture(scope="session")
def alembic_engine(sync_db_engine: Engine) -> Engine:
    """Proxy sync_db_engine to pytest_alembic (make it as a default engine)."""
    return sync_db_engine


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    """Initialize pytest_alembic Config."""
    return Config()


@pytest.fixture(scope="session")
def alembic_runner(alembic_config: Config, alembic_engine: Engine) -> Generator[runner, None, None]:
    """Setup runner for pytest_alembic (combine Config and engine)."""
    config = Config.from_raw_config(alembic_config)
    with runner(config=config, engine=alembic_engine) as alembic_runner:
        yield alembic_runner


@pytest.fixture(scope="session", autouse=True)
def _create_database() -> Generator[None, None, None]:
    """Recreates `test` database for tests."""
    con = psycopg2.connect(
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}"
    )

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = con.cursor()
    close_all_sessions()
    cursor.execute(f"""DROP DATABASE IF EXISTS {settings.DB_NAME};""")
    cursor.execute(f"""CREATE DATABASE {settings.DB_NAME};""")
    yield
    close_all_sessions()
    cursor.execute(f"""DROP DATABASE IF EXISTS {settings.DB_NAME};""")


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations(
    _create_database: None,
    alembic_runner: runner,
    alembic_engine: Engine,
) -> Generator[None, None, None]:
    """Applies all migrations from base to head (via pytest_alembic)."""
    alembic_runner.migrate_up_to(revision="head")
    yield
    alembic_runner.migrate_down_to(revision="base")


@pytest.fixture(scope="session")
def sync_postgres_config() -> str:
    return PostgresDsn.build(
        scheme='postgresql',
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        path=settings.DB_NAME,
    ).unicode_string()


@pytest.fixture(scope="session")
def sync_db_engine(sync_postgres_config: str) -> Engine:
    """Create sync database engine and dispose it after all tests.

    Yields:
        engine (Engine): SQLAlchemy Engine instance.
    """
    engine = create_engine(url=sync_postgres_config, echo=settings.ECHO_SQL)
    try:
        yield engine
    finally:
        close_all_sessions()
        engine.dispose()


@pytest.mark.asyncio
@pytest.fixture()
async def app_fixture(async_db_session: AsyncSession) -> FastAPI:
    """Overrides dependencies for FastAPI and returns FastAPI instance (app).

    Yields:
        app (fastapi.FastAPI): Instance of FastAPI ASGI application.
    """

    async def override_get_async_session() -> AsyncSession:
        """Replace `get_async_session` dependency with AsyncSession from `db_session` fixture."""
        return async_db_session

    app.dependency_overrides[get_session] = override_get_async_session
    return app


@pytest.mark.asyncio
@pytest.fixture
async def client(app_fixture: FastAPI, base_url: str) -> AsyncClient:
    async with AsyncClient(app=app_fixture, timeout=900, base_url=base_url) as client:
        yield client


@pytest.fixture
def base_user() -> dict:
    return {
        "email": "andr@mail.ru",
        "password": "fylhtq5678",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "username": "andrey",
        "first_name": "adnr",
        "last_name": "andr",
        "patronymic": "andr"
    }
