"""
Pytest configuration and fixtures.
"""

import sys
import pytest
from pathlib import Path

# Add the backend root directory to Python path so config module can be imported
backend_root = Path(__file__).parent.parent.parent.resolve()
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

# Also add the src directory for relative imports
src_root = Path(__file__).parent.parent.resolve()
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

# Set up environment variables to prevent some import issues
import os
os.environ["TESTING"] = "1"
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret")

# Import models at pytest session level to avoid redefinition issues
from models import *
