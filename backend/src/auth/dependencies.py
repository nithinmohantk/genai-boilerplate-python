"""
Authentication dependencies for FastAPI endpoints.
"""

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from models.auth import Tenant, User, UserRole
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Current authenticated user context."""

    def __init__(self, user: User, token_payload: dict):
        self.user = user
        self.token_payload = token_payload

    @property
    def user_id(self) -> UUID:
        return self.user.id

    @property
    def tenant_id(self) -> UUID:
        return self.user.tenant_id

    @property
    def email(self) -> str:
        return self.user.email

    @property
    def role(self) -> UserRole:
        return UserRole(self.user.role)

    @property
    def is_tenant_admin(self) -> bool:
        return self.role in [UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN]

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN

    @property
    def tenant(self) -> Tenant:
        return self.user.tenant


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None

    try:
        auth_service = AuthService(db)
        token_payload = await auth_service.verify_access_token(credentials.credentials)

        if not token_payload:
            return None

        user_id = UUID(token_payload["user_id"])
        user = await auth_service.get_user_by_id(user_id)

        if not user or not user.is_active:
            return None

        return CurrentUser(user, token_payload)

    except Exception as e:
        logger.warning(f"Error verifying token: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Get current authenticated user (required)."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_service = AuthService(db)
        token_payload = await auth_service.verify_access_token(credentials.credentials)

        if not token_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = UUID(token_payload["user_id"])
        user = await auth_service.get_user_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if tenant is active
        if user.tenant.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is not active"
            )

        return CurrentUser(user, token_payload)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        ) from e


async def require_tenant_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require tenant admin or higher role."""
    if not current_user.is_tenant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tenant admin access required"
        )
    return current_user


async def require_super_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require super admin role."""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required"
        )
    return current_user


def require_role(required_role: UserRole):
    """Create a dependency that requires a specific role."""

    async def role_dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role != required_role and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role} required",
            )
        return current_user

    return role_dependency


def require_any_role(*roles: UserRole):
    """Create a dependency that requires any of the specified roles."""

    async def role_dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in roles and not current_user.is_super_admin:
            roles_str = ", ".join(roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {roles_str}",
            )
        return current_user

    return role_dependency


async def get_tenant_from_domain(
    tenant_domain: str, db: AsyncSession = Depends(get_db)
) -> Tenant:
    """Get tenant by domain."""
    auth_service = AuthService(db)
    tenant = await auth_service.get_tenant_by_domain(tenant_domain)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    return tenant


class TenantScope:
    """Tenant scoped dependency to ensure users only access their tenant data."""

    def __init__(self, allow_cross_tenant_super_admin: bool = True):
        self.allow_cross_tenant_super_admin = allow_cross_tenant_super_admin

    async def __call__(
        self, tenant_id: UUID, current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        """Verify user has access to the specified tenant."""
        # Super admins can access any tenant if allowed
        if self.allow_cross_tenant_super_admin and current_user.is_super_admin:
            return current_user

        # Regular users can only access their own tenant
        if current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this tenant",
            )

        return current_user


# Common dependency instances
tenant_scope = TenantScope()
tenant_scope_strict = TenantScope(allow_cross_tenant_super_admin=False)
