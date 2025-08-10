"""
Navigation BDD test configuration and runner.
This module sets up and runs comprehensive navigation tests using pytest-bdd.
"""

from pytest_bdd import scenarios

# Load all scenarios from the navigation feature file
scenarios('../features/navigation.feature')

# Additional test configuration can be added here if needed
pytest_plugins = ['step_definitions.test_navigation_steps']
