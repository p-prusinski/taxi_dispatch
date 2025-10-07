from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from config import settings
from database import get_db
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture
def client(override_get_db_dependency: None) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://taxi")


@pytest.fixture(scope="session")
def database_url() -> URL:
    db_name = "test_taxi"
    host = "127.0.0.1"
    port = 5432
    return URL.create(
        "postgresql+asyncpg",
        settings.postgres_user,
        settings.postgres_password.get_secret_value(),
        host,
        port,
        db_name,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_test_database(database_url: URL) -> AsyncGenerator[None, URL]:
    await create_database(database_url)
    await make_migration(database_url)
    yield
    await drop_database(database_url)


async def create_database(url: URL) -> None:
    database_name = url.database
    real_db_url = url.set(database=settings.postgres_db)
    engine = create_async_engine(real_db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        c = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = c.scalar() == 1

    if database_exists:
        await drop_database(url)

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{database_name}" ENCODING "utf8" TEMPLATE template1'
            )
        )
    await engine.dispose()


async def make_migration(url: URL) -> None:
    alembic_cfg = Config("backend/alembic.ini")
    db_url_str = url.render_as_string(hide_password=False)
    # special characters are %-encoded
    # values in ini files are interpolated; must escape % with %%
    db_url_str = db_url_str.replace("%", "%%")
    alembic_cfg.set_section_option("alembic", "sqlalchemy.url", db_url_str)
    alembic_cfg.set_section_option("alembic", "script_location", "backend/migrations")

    engine = create_async_engine(url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: command.upgrade(alembic_cfg, "head"))
    await engine.dispose()


async def drop_database(url: URL) -> None:
    real_db_url = url.set(database=settings.postgres_db)
    engine = create_async_engine(real_db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text(f'DROP DATABASE "{url.database}"'))


@pytest_asyncio.fixture()
async def sql_engine(database_url: URL) -> AsyncGenerator[AsyncEngine, URL]:
    engine = create_async_engine(database_url)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(
    sql_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, AsyncEngine]:
    """
    Returns an async SQLAlchemy session with a SAVEPOINT,
    and the rollback to it after the test completes
    """
    connection = await sql_engine.connect()
    transaction = await connection.begin()

    async with async_sessionmaker(connection, expire_on_commit=False)() as session:
        await restart_autoincrement_pk(session)
        try:
            yield session
        finally:
            if transaction.is_active:
                await transaction.rollback()
            await session.close()
            await connection.close()


@pytest_asyncio.fixture()
async def override_get_db_dependency(db_session: AsyncSession) -> None:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db


async def restart_autoincrement_pk(session: AsyncSession) -> None:
    transaction = await session.execute(
        text("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S'")
    )
    for sequence in transaction.scalars().all():
        await session.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
