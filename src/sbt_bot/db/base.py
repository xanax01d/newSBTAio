from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def create_engine_and_sessionmaker(
    database_url: str,
    *,
    echo: bool = False,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create async SQLAlchemy engine and session factory."""
    engine = create_async_engine(database_url, echo=echo, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_factory
