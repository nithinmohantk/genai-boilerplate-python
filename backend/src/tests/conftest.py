"""
Pytest configuration and fixtures.
"""

import os
import sys
from pathlib import Path

# Add the backend root directory to Python path so config module can be imported
backend_root = Path(__file__).parent.parent.parent.resolve()
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

# Also add the src directory for relative imports
src_root = Path(__file__).parent.parent.resolve()  
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))
