"""
Database session dependencies and utilities.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting database session."""
    async with get_db_session() as session:
        yield session


# Type alias for database session dependency
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
