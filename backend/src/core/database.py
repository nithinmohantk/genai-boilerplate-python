"""
Database configuration and connection management.
Handles SQLAlchemy setup, session management, and database operations.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import settings

# Database metadata and base class
metadata = MetaData()


class Base(DeclarativeBase):
    """Base class for all database models."""

    metadata = metadata


# Global variables for database connections
async_engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None
sync_engine = None
sync_session_factory = None


async def init_db() -> None:
    """Initialize database connections and create tables."""
    global async_engine, async_session_factory, sync_engine, sync_session_factory

    try:
        # Create async engine for database operations
        database_url = settings.database_url
        if database_url.startswith("postgresql://"):
            # Convert to asyncpg for async operations
            async_database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        else:
            async_database_url = database_url

        async_engine = create_async_engine(
            async_database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections after 5 minutes
        )

        # Create async session factory
        async_session_factory = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Create sync engine for migrations and synchronous operations
        sync_engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        # Create sync session factory
        sync_session_factory = sessionmaker(
            bind=sync_engine,
            class_=Session,
            expire_on_commit=False,
        )

        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """Close database connections."""
    global async_engine, sync_engine

    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("Async database engine disposed")

        if sync_engine:
            sync_engine.dispose()
            logger.info("Sync database engine disposed")

    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session context manager."""
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_sync_session() -> AsyncGenerator[Session, None]:
    """Get sync database session context manager."""
    if not sync_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    with sync_session_factory() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting database session."""
    async with get_async_session() as session:
        yield session


def get_sync_db_session() -> Session:
    """Get synchronous database session (for migrations, etc.)."""
    if not sync_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    return sync_session_factory()


# Health check function
async def check_database_health() -> bool:
    """Check if database connection is healthy."""
    try:
        if not async_engine:
            return False

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
