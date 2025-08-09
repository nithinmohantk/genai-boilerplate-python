"""
Authentication API endpoints for login, registration, and user management.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    CurrentUser,
    get_current_user,
    require_super_admin,
    security,
)
from database.session import get_db
from models.auth import (
    AuthProviderCallback,
    LoginRequest,
    TenantCreate,
    TenantResponse,
    TenantUpdate,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    try:
        auth_service = AuthService(db)

        # Authenticate user
        user = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            tenant_domain=login_data.tenant_domain,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified"
            )

        # Create tokens
        access_token = auth_service.create_access_token(user)
        refresh_token = await auth_service.create_refresh_token(
            user=user,
            device_info={
                "user_agent": request.headers.get("user-agent"),
                "ip_address": request.client.host if request.client else None,
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        logger.info(f"User {user.id} logged in successfully")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        ) from e


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    try:
        auth_service = AuthService(db)

        # Check if tenant exists
        tenant = await auth_service.get_tenant_by_id(user_data.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant"
            )

        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(
            user_data.email, user_data.tenant_id
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        # Create user
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            tenant_id=user_data.tenant_id,
            username=user_data.username,
            full_name=user_data.full_name,
            role=user_data.role,
            timezone=user_data.timezone,
            language=user_data.language,
            preferences=user_data.preferences,
        )

        logger.info(f"User {user.id} registered successfully")

        return UserResponse.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        ) from e


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required"
        )

    try:
        auth_service = AuthService(db)

        result = await auth_service.refresh_access_token(credentials.credentials)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        access_token, refresh_token = result

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        ) from e


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Logout user and revoke refresh token."""
    if not credentials:
        return {"message": "Logged out successfully"}

    try:
        auth_service = AuthService(db)
        await auth_service.revoke_refresh_token(credentials.credentials)

        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.from_orm(current_user.user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_updates: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    try:
        auth_service = AuthService(db)

        updated_user = await auth_service.update_user_profile(
            user_id=current_user.user_id, updates=user_updates.dict(exclude_unset=True)
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        logger.info(f"User {current_user.user_id} profile updated")

        return UserResponse.from_orm(updated_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        ) from e


@router.post("/change-password")
async def change_password(
    password_data: dict[str, str],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")

    if not old_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both old_password and new_password are required",
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )

    try:
        auth_service = AuthService(db)

        success = await auth_service.change_password(
            user_id=current_user.user_id,
            old_password=old_password,
            new_password=new_password,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
            )

        logger.info(f"User {current_user.user_id} password changed")

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed",
        ) from e


@router.post("/revoke-all-tokens")
async def revoke_all_tokens(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all refresh tokens for current user."""
    try:
        auth_service = AuthService(db)
        await auth_service.revoke_all_user_tokens(current_user.user_id)

        logger.info(f"All tokens revoked for user {current_user.user_id}")

        return {"message": "All tokens revoked successfully"}

    except Exception as e:
        logger.error(f"Token revocation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token revocation failed",
        ) from e


# Tenant Management (Admin endpoints)


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: CurrentUser = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant (Super admin only)."""
    try:
        auth_service = AuthService(db)

        # Check if tenant domain already exists
        existing_tenant = await auth_service.get_tenant_by_domain(tenant_data.domain)
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant domain already exists",
            )

        tenant = await auth_service.create_tenant(
            name=tenant_data.name,
            domain=tenant_data.domain,
            created_by=current_user.user_id,
            status=tenant_data.status,
            settings=tenant_data.settings,
            branding=tenant_data.branding,
            limits=tenant_data.limits,
        )

        logger.info(f"Tenant {tenant.id} created by {current_user.user_id}")

        return TenantResponse.from_orm(tenant)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tenant creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tenant creation failed",
        ) from e


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tenant information."""
    # Users can only see their own tenant unless super admin
    if not current_user.is_super_admin and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        auth_service = AuthService(db)
        tenant = await auth_service.get_tenant_by_id(tenant_id)

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )

        return TenantResponse.from_orm(tenant)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant",
        ) from e


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_updates: TenantUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update tenant information."""
    # Only tenant admins can update their tenant, super admins can update any
    if not current_user.is_super_admin:
        if current_user.tenant_id != tenant_id or not current_user.is_tenant_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    try:
        auth_service = AuthService(db)
        tenant = await auth_service.get_tenant_by_id(tenant_id)

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )

        # Update tenant
        update_data = tenant_updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(tenant, field):
                setattr(tenant, field, value)

        await db.commit()
        await db.refresh(tenant)

        logger.info(f"Tenant {tenant_id} updated by {current_user.user_id}")

        return TenantResponse.from_orm(tenant)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Tenant update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tenant update failed",
        ) from e


# OAuth endpoints (placeholder for now)


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, tenant_domain: str | None = None):
    """Initiate OAuth login flow."""
    # TODO: Implement OAuth login initiation
    # This would redirect to the OAuth provider's authorization URL
    return {
        "message": f"OAuth login for {provider} not yet implemented",
        "provider": provider,
        "tenant_domain": tenant_domain,
    }


@router.post("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    callback_data: AuthProviderCallback,
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth callback."""
    # TODO: Implement OAuth callback handling
    # This would:
    # 1. Exchange code for access token
    # 2. Get user info from provider
    # 3. Create or link user account
    # 4. Return JWT tokens
    return {
        "message": f"OAuth callback for {provider} not yet implemented",
        "provider": provider,
        "code": callback_data.code,
    }
