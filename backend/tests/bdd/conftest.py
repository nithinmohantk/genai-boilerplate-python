"""
BDD test configuration for backend tests.
"""

import asyncio
import os
import sys
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from core.database import Base, get_db_session
from main import app
from models import *  # Import all models to ensure SQLAlchemy relationships work


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="session")
def test_database():
    """Create a test database."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db

    yield TestingSessionLocal

    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_database):
    """Create a database session for each test."""
    session = test_database()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["JWT_SECRET"] = "test_jwt_secret"

    # Create temporary directories for testing
    temp_dir = tempfile.mkdtemp()
    os.environ["DATA_DIR"] = temp_dir

    yield

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ai_service():
    """Mock AI service responses for testing."""

    class MockAIService:
        def generate_response(self, message: str, context: str = None) -> str:
            return f"AI Response to: {message}"

        def is_model_available(self, model: str) -> bool:
            return model != "unavailable-model"

    return MockAIService()


@pytest.fixture
def websocket_client():
    """Create a WebSocket client for testing."""
    from fastapi.testclient import TestClient

    return TestClient(app)
