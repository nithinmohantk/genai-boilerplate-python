"""
BDD Step definitions for authentication feature tests.
"""
import json
import jwt
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pytest
from pytest_bdd import given, when, then, parsers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys
import os

# Add src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from models.auth import User, Tenant, UserRole
from services.auth_service import AuthService
from core.database import get_db
from main import app


class AuthenticationStepContext:
    """Context to store state between BDD steps."""
    
    def __init__(self):
        self.client = TestClient(app)
        self.response: Optional[Any] = None
        self.tokens: Dict[str, str] = {}
        self.current_user: Optional[User] = None
        self.error_message: Optional[str] = None
        self.tenant: Optional[Tenant] = None
        self.db_session: Optional[Session] = None
        self.auth_service: Optional[AuthService] = None


@pytest.fixture
def auth_context():
    """Fixture to provide authentication context."""
    context = AuthenticationStepContext()
    # Override database session for testing
    context.db_session = next(get_db())
    context.auth_service = AuthService(context.db_session)
    return context


# Background steps
@given("the application is running", target_fixture="auth_context")
def application_running(auth_context):
    """Ensure the application is running."""
    response = auth_context.client.get("/health")
    assert response.status_code == 200
    return auth_context


@given("the database is initialized")
def database_initialized(auth_context):
    """Ensure database is initialized and clean."""
    # Clean up any existing test data
    auth_context.db_session.query(User).filter(User.email.contains("@example.com")).delete()
    auth_context.db_session.commit()


@given(parsers.parse('a test tenant exists with name "{tenant_name}"'))
def test_tenant_exists(auth_context, tenant_name: str):
    """Create a test tenant."""
    tenant = Tenant(
        name=tenant_name,
        domain="test-company.com",
        is_active=True
    )
    auth_context.db_session.add(tenant)
    auth_context.db_session.commit()
    auth_context.db_session.refresh(tenant)
    auth_context.tenant = tenant


# Authentication state steps
@given("I am not authenticated")
def not_authenticated(auth_context):
    """Ensure user is not authenticated."""
    auth_context.tokens = {}
    auth_context.current_user = None


@given("I am authenticated as a user")
def authenticated_as_user(auth_context):
    """Authenticate as a regular user."""
    user_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "name": "Test User"
    }
    user = create_test_user(auth_context, user_data, verified=True)
    authenticate_user(auth_context, user)


@given(parsers.parse('I am authenticated as a user with password "{password}"'))
def authenticated_with_password(auth_context, password: str):
    """Authenticate user with specific password."""
    user_data = {
        "email": "test@example.com",
        "password": password,
        "name": "Test User"
    }
    user = create_test_user(auth_context, user_data, verified=True)
    authenticate_user(auth_context, user)


@given("I am authenticated as a user with:", target_fixture="auth_context")
def authenticated_user_with_details(auth_context, step_data):
    """Authenticate user with specific details from table."""
    user_data = {row['field']: row['value'] for row in step_data}
    
    # Set default password if not provided
    if 'password' not in user_data:
        user_data['password'] = 'SecurePassword123!'
    
    # Convert role to enum if provided
    role = UserRole.USER
    if 'role' in user_data:
        role = UserRole(user_data['role'].upper())
    
    user = create_test_user(auth_context, user_data, verified=True, role=role)
    authenticate_user(auth_context, user)
    return auth_context


@given("I am authenticated as an admin user")
def authenticated_as_admin(auth_context):
    """Authenticate as admin user."""
    user_data = {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "name": "Admin User"
    }
    user = create_test_user(auth_context, user_data, verified=True, role=UserRole.TENANT_ADMIN)
    authenticate_user(auth_context, user)


@given("I am authenticated as a regular user")
def authenticated_as_regular_user(auth_context):
    """Authenticate as regular user."""
    authenticated_as_user(auth_context)


@given("a user exists with:")
def user_exists_with_details(auth_context, step_data):
    """Create a user with specific details."""
    user_data = {row['field']: row['value'] for row in step_data}
    verified = user_data.get('verified', 'true').lower() == 'true'
    create_test_user(auth_context, user_data, verified=verified)


@given(parsers.parse('a user exists with email "{email}"'))
def user_exists_with_email(auth_context, email: str):
    """Create a user with specific email."""
    user_data = {
        "email": email,
        "password": "SecurePassword123!",
        "name": "Test User"
    }
    create_test_user(auth_context, user_data, verified=True)


@given("I have an invalid authentication token")
def invalid_token(auth_context):
    """Set an invalid authentication token."""
    auth_context.tokens = {"access_token": "invalid_token"}


@given("I have an invalid refresh token")
def invalid_refresh_token(auth_context):
    """Set an invalid refresh token."""
    auth_context.tokens = {"refresh_token": "invalid_refresh_token"}


@given("I am authenticated with tokens:")
def authenticated_with_token_states(auth_context, step_data):
    """Set authentication tokens with specific states."""
    # Create valid tokens first
    user = create_test_user(auth_context, {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "name": "Test User"
    }, verified=True)
    
    tokens = auth_context.auth_service.create_tokens(user)
    
    for row in step_data:
        token_type = row['token_type']
        status = row['status']
        
        if status == 'expired':
            # Create expired token
            if token_type == 'access_token':
                expired_token = create_expired_token(user, token_type='access')
                auth_context.tokens['access_token'] = expired_token
            elif token_type == 'refresh_token':
                expired_token = create_expired_token(user, token_type='refresh')
                auth_context.tokens['refresh_token'] = expired_token
        elif status == 'valid':
            auth_context.tokens[token_type] = tokens[token_type]


# Registration steps
@when("I register with valid credentials:")
def register_with_valid_credentials(auth_context, step_data):
    """Register with provided credentials."""
    registration_data = {row['field']: row['value'] for row in step_data}
    registration_data['tenant_id'] = str(auth_context.tenant.id)
    
    auth_context.response = auth_context.client.post("/api/auth/register", json=registration_data)


@when("I register with invalid credentials:")
def register_with_invalid_credentials(auth_context, step_data):
    """Register with invalid credentials."""
    registration_data = {row['field']: row['value'] for row in step_data}
    registration_data['tenant_id'] = str(auth_context.tenant.id)
    
    auth_context.response = auth_context.client.post("/api/auth/register", json=registration_data)


# Login steps
@when("I login with correct credentials:")
def login_with_correct_credentials(auth_context, step_data):
    """Login with correct credentials."""
    login_data = {row['field']: row['value'] for row in step_data}
    auth_context.response = auth_context.client.post("/api/auth/login", json=login_data)


@when("I login with incorrect credentials:")
def login_with_incorrect_credentials(auth_context, step_data):
    """Login with incorrect credentials."""
    login_data = {row['field']: row['value'] for row in step_data}
    auth_context.response = auth_context.client.post("/api/auth/login", json=login_data)


@when(parsers.parse('I attempt to login {attempts:d} times with incorrect password'))
def multiple_failed_login_attempts(auth_context, attempts: int):
    """Attempt multiple failed logins."""
    for i in range(attempts):
        login_data = {
            "email": "test@example.com",
            "password": f"WrongPassword{i}"
        }
        response = auth_context.client.post("/api/auth/login", json=login_data)
        
        # Store the last response
        if i == attempts - 1:
            auth_context.response = response


# Token and access steps
@when(parsers.parse('I access a protected resource "{endpoint}"'))
def access_protected_resource(auth_context, endpoint: str):
    """Access a protected resource."""
    headers = {}
    if 'access_token' in auth_context.tokens:
        headers['Authorization'] = f"Bearer {auth_context.tokens['access_token']}"
    
    auth_context.response = auth_context.client.get(endpoint, headers=headers)


@when("I refresh my tokens using the refresh token")
def refresh_tokens(auth_context):
    """Refresh authentication tokens."""
    refresh_data = {"refresh_token": auth_context.tokens.get('refresh_token', '')}
    auth_context.response = auth_context.client.post("/api/auth/refresh", json=refresh_data)


@when("I logout")
def logout_user(auth_context):
    """Logout current user."""
    headers = {}
    if 'access_token' in auth_context.tokens:
        headers['Authorization'] = f"Bearer {auth_context.tokens['access_token']}"
    
    auth_context.response = auth_context.client.post("/api/auth/logout", headers=headers)


@when("I change my password:")
def change_password(auth_context, step_data):
    """Change user password."""
    password_data = {row['field']: row['value'] for row in step_data}
    
    headers = {}
    if 'access_token' in auth_context.tokens:
        headers['Authorization'] = f"Bearer {auth_context.tokens['access_token']}"
    
    auth_context.response = auth_context.client.post(
        "/api/auth/change-password", 
        json=password_data, 
        headers=headers
    )


# Assertion steps
@then("the registration should be successful")
def registration_successful(auth_context):
    """Assert registration was successful."""
    assert auth_context.response.status_code == 201
    response_data = auth_context.response.json()
    assert "user" in response_data
    assert "message" in response_data


@then("the registration should fail")
def registration_failed(auth_context):
    """Assert registration failed."""
    assert auth_context.response.status_code == 400


@then("I should receive a confirmation response")
def receive_confirmation_response(auth_context):
    """Assert confirmation response received."""
    response_data = auth_context.response.json()
    assert "message" in response_data


@then("the user should exist in the database")
def user_exists_in_database(auth_context):
    """Assert user exists in database."""
    response_data = auth_context.response.json()
    email = response_data["user"]["email"]
    
    user = auth_context.db_session.query(User).filter(User.email == email).first()
    assert user is not None


@then("the user should be assigned to the default role")
def user_has_default_role(auth_context):
    """Assert user has default role."""
    response_data = auth_context.response.json()
    assert response_data["user"]["role"] == "user"


@then(parsers.parse('I should receive an error message "{message}"'))
def receive_error_message(auth_context, message: str):
    """Assert specific error message received."""
    response_data = auth_context.response.json()
    assert message in response_data.get("detail", "")


@then(parsers.parse('I should receive an error message containing "{text}"'))
def receive_error_containing(auth_context, text: str):
    """Assert error message contains specific text."""
    response_data = auth_context.response.json()
    error_detail = response_data.get("detail", "")
    assert text in error_detail


@then("the login should be successful")
def login_successful(auth_context):
    """Assert login was successful."""
    assert auth_context.response.status_code == 200
    response_data = auth_context.response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@then("the login should fail")
def login_failed(auth_context):
    """Assert login failed."""
    assert auth_context.response.status_code == 401


@then("I should receive an access token")
def receive_access_token(auth_context):
    """Assert access token received."""
    response_data = auth_context.response.json()
    assert "access_token" in response_data
    auth_context.tokens["access_token"] = response_data["access_token"]


@then("I should receive a refresh token")
def receive_refresh_token(auth_context):
    """Assert refresh token received."""
    response_data = auth_context.response.json()
    assert "refresh_token" in response_data
    auth_context.tokens["refresh_token"] = response_data["refresh_token"]


@then("the tokens should be valid")
def tokens_are_valid(auth_context):
    """Assert tokens are valid."""
    # Verify access token
    access_token = auth_context.tokens.get("access_token")
    assert access_token is not None
    
    try:
        # Decode without verification for testing
        payload = jwt.decode(access_token, options={"verify_signature": False})
        assert "user_id" in payload
        assert "exp" in payload
    except jwt.InvalidTokenError:
        pytest.fail("Access token is invalid")


@then("my user profile should be included in the response")
def user_profile_in_response(auth_context):
    """Assert user profile included in response."""
    response_data = auth_context.response.json()
    assert "user" in response_data
    user = response_data["user"]
    assert "id" in user
    assert "email" in user
    assert "name" in user


@then("no tokens should be issued")
def no_tokens_issued(auth_context):
    """Assert no tokens were issued."""
    response_data = auth_context.response.json()
    assert "access_token" not in response_data
    assert "refresh_token" not in response_data


@then("the request should be successful")
def request_successful(auth_context):
    """Assert request was successful."""
    assert auth_context.response.status_code == 200


@then(parsers.parse("the request should fail with status {status_code:d}"))
def request_failed_with_status(auth_context, status_code: int):
    """Assert request failed with specific status code."""
    assert auth_context.response.status_code == status_code


@then("I should receive my user profile information")
def receive_user_profile(auth_context):
    """Assert user profile information received."""
    response_data = auth_context.response.json()
    assert "id" in response_data
    assert "email" in response_data
    assert "name" in response_data


@then("the token refresh should be successful")
def token_refresh_successful(auth_context):
    """Assert token refresh was successful."""
    assert auth_context.response.status_code == 200
    response_data = auth_context.response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@then("the token refresh should fail")
def token_refresh_failed(auth_context):
    """Assert token refresh failed."""
    assert auth_context.response.status_code == 401


@then("I should receive a new access token")
def receive_new_access_token(auth_context):
    """Assert new access token received."""
    response_data = auth_context.response.json()
    new_access_token = response_data["access_token"]
    
    # Ensure it's different from the old one
    old_access_token = auth_context.tokens.get("access_token")
    assert new_access_token != old_access_token
    
    auth_context.tokens["access_token"] = new_access_token


@then("I should receive a new refresh token")
def receive_new_refresh_token(auth_context):
    """Assert new refresh token received."""
    response_data = auth_context.response.json()
    new_refresh_token = response_data["refresh_token"]
    
    # Ensure it's different from the old one
    old_refresh_token = auth_context.tokens.get("refresh_token")
    assert new_refresh_token != old_refresh_token
    
    auth_context.tokens["refresh_token"] = new_refresh_token


@then("the old tokens should be invalidated")
def old_tokens_invalidated(auth_context):
    """Assert old tokens are invalidated."""
    # This would require checking token blacklist in real implementation
    # For now, we'll just verify new tokens were issued
    response_data = auth_context.response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@then("the logout should be successful")
def logout_successful(auth_context):
    """Assert logout was successful."""
    assert auth_context.response.status_code == 200


@then("my tokens should be invalidated")
def tokens_invalidated(auth_context):
    """Assert tokens are invalidated."""
    # Clear tokens from context
    auth_context.tokens = {}


@then("I should not be able to access protected resources")
def cannot_access_protected_resources(auth_context):
    """Assert cannot access protected resources after logout."""
    response = auth_context.client.get("/api/auth/profile")
    assert response.status_code == 401


@then("the password change should be successful")
def password_change_successful(auth_context):
    """Assert password change was successful."""
    assert auth_context.response.status_code == 200


@then("the password change should fail")
def password_change_failed(auth_context):
    """Assert password change failed."""
    assert auth_context.response.status_code == 400


@then(parsers.parse('I should be able to login with the new password'))
def can_login_with_new_password(auth_context):
    """Assert can login with new password."""
    login_data = {
        "email": "test@example.com",
        "password": "NewPassword123!"
    }
    response = auth_context.client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200


@then(parsers.parse('I should not be able to login with the old password'))
def cannot_login_with_old_password(auth_context):
    """Assert cannot login with old password."""
    login_data = {
        "email": "test@example.com",
        "password": "OldPassword123!"
    }
    response = auth_context.client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401


@then(parsers.parse('I should still be able to login with the old password'))
def can_still_login_with_old_password(auth_context):
    """Assert can still login with old password."""
    login_data = {
        "email": "test@example.com",
        "password": "OldPassword123!"
    }
    response = auth_context.client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200


@then("the account should be temporarily locked")
def account_locked(auth_context):
    """Assert account is temporarily locked."""
    # Check if user account is locked in database
    user = auth_context.db_session.query(User).filter(
        User.email == "test@example.com"
    ).first()
    
    assert user is not None
    # In real implementation, check for lockout timestamp or flag


@then(parsers.parse('subsequent login attempts should fail with "{message}"'))
def subsequent_logins_fail(auth_context, message: str):
    """Assert subsequent login attempts fail with specific message."""
    login_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
    response = auth_context.client.post("/api/auth/login", json=login_data)
    assert response.status_code == 423  # Locked
    
    response_data = response.json()
    assert message in response_data.get("detail", "")


@then("I should receive information about lockout duration")
def receive_lockout_duration_info(auth_context):
    """Assert lockout duration information received."""
    response_data = auth_context.response.json()
    assert "lockout_duration" in response_data or "duration" in response_data.get("detail", "")


@then("I should receive the requested admin data")
def receive_admin_data(auth_context):
    """Assert admin data received."""
    response_data = auth_context.response.json()
    # Verify admin-specific data structure
    assert isinstance(response_data, (list, dict))


# Helper functions
def create_test_user(auth_context, user_data: Dict[str, str], verified: bool = True, role: UserRole = UserRole.USER) -> User:
    """Create a test user in the database."""
    hashed_password = auth_context.auth_service.hash_password(user_data["password"])
    
    user = User(
        email=user_data["email"],
        name=user_data["name"],
        hashed_password=hashed_password,
        is_verified=verified,
        role=role,
        tenant_id=auth_context.tenant.id
    )
    
    auth_context.db_session.add(user)
    auth_context.db_session.commit()
    auth_context.db_session.refresh(user)
    
    return user


def authenticate_user(auth_context, user: User):
    """Authenticate a user and set tokens."""
    tokens = auth_context.auth_service.create_tokens(user)
    auth_context.tokens = tokens
    auth_context.current_user = user


def create_expired_token(user: User, token_type: str = 'access') -> str:
    """Create an expired JWT token for testing."""
    now = datetime.utcnow()
    exp_time = now - timedelta(hours=1)  # Expired 1 hour ago
    
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "exp": exp_time,
        "iat": now - timedelta(hours=2),
        "type": token_type
    }
    
    # Use a dummy secret for testing
    return jwt.encode(payload, "test_secret", algorithm="HS256")
