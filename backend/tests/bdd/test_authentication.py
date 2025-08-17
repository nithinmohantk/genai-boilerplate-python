"""
BDD test runner for authentication feature.
"""

import pytest
from pytest_bdd import scenarios

# Load all scenarios from the authentication feature file
scenarios("../features/authentication.feature")


# Additional pytest marks for organization
pytestmark = [
    pytest.mark.bdd,
    pytest.mark.authentication,
]


def test_authentication_scenarios():
    """
    This function will be automatically populated by pytest-bdd
    with individual test functions for each scenario.
    """
    pass
