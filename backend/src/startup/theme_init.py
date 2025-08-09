"""
Startup initialization for themes and database setup.
"""

import asyncio
import logging

from database.connection import get_db_session
from services.theme_init_service import ThemeInitService
from services.theme_service import ThemeService

logger = logging.getLogger(__name__)


async def initialize_themes():
    """Initialize default themes on startup."""
    try:
        logger.info("Starting theme initialization...")

        # Get database session
        async with get_db_session() as session:
            # Initialize services
            theme_service = ThemeService(session)
            theme_init_service = ThemeInitService(theme_service)

            # Create default themes
            created_themes = await theme_init_service.create_default_themes()

            logger.info(
                f"Theme initialization completed. Created {len(created_themes)} themes"
            )
            return created_themes

    except Exception as e:
        logger.error(f"Theme initialization failed: {e}")
        raise


async def startup_initialization():
    """Complete startup initialization for the application."""
    try:
        logger.info("Starting application initialization...")

        # Initialize themes
        await initialize_themes()

        logger.info("Application initialization completed successfully")

    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise


if __name__ == "__main__":
    # For testing purposes
    asyncio.run(startup_initialization())
