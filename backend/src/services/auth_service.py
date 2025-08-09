"""
Authentication service with JWT, OAuth, and multi-tenancy support.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.settings import settings
from models.auth import (
    AuthProvider,
    RefreshToken,
    Tenant,
    TenantStatus,
    User,
    UserAuthProvider,
    UserRole,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management and JWT tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30

    async def authenticate_user(
        self, email: str, password: str, tenant_domain: str | None = None
    ) -> User | None:
        """Authenticate user with email and password."""
        try:
            # Get tenant
            tenant = await self.get_tenant_by_domain(tenant_domain or "default")
            if not tenant or tenant.status != TenantStatus.ACTIVE:
                return None

            # Get user
            query = (
                select(User)
                .options(selectinload(User.tenant))
                .where(User.email == email, User.tenant_id == tenant.id)
            )
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                return None

            # Check password
            if not user.hashed_password:
                return None  # User might only have OAuth

            if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
                return None

            # Update last login
            user.last_login_at = datetime.now()
            await self.db.commit()

            return user

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    async def create_user(
        self,
        email: str,
        password: str | None,
        tenant_id: UUID,
        username: str | None = None,
        full_name: str | None = None,
        role: UserRole = UserRole.TENANT_USER,
        **kwargs,
    ) -> User:
        """Create a new user."""
        try:
            # Hash password if provided
            hashed_password = None
            if password:
                hashed_password = bcrypt.hashpw(
                    password.encode(), bcrypt.gensalt()
                ).decode()

            user = User(
                tenant_id=tenant_id,
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password,
                role=role,
                is_verified=False,  # Email verification required
                **kwargs,
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Created user {user.id} with email {email}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
            )

    async def create_tenant(
        self, name: str, domain: str, created_by: UUID | None = None, **kwargs
    ) -> Tenant:
        """Create a new tenant."""
        try:
            tenant = Tenant(name=name, domain=domain, created_by=created_by, **kwargs)

            self.db.add(tenant)
            await self.db.commit()
            await self.db.refresh(tenant)

            logger.info(f"Created tenant {tenant.id} with domain {domain}")
            return tenant

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating tenant: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create tenant",
            )

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        try:
            query = (
                select(User)
                .options(selectinload(User.tenant))
                .where(User.id == user_id)
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    async def get_user_by_email(self, email: str, tenant_id: UUID) -> User | None:
        """Get user by email within tenant."""
        try:
            query = (
                select(User)
                .options(selectinload(User.tenant))
                .where(User.email == email, User.tenant_id == tenant_id)
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def get_tenant_by_domain(self, domain: str) -> Tenant | None:
        """Get tenant by domain."""
        try:
            query = select(Tenant).where(Tenant.domain == domain)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting tenant by domain: {e}")
            return None

    async def get_tenant_by_id(self, tenant_id: UUID) -> Tenant | None:
        """Get tenant by ID."""
        try:
            query = select(Tenant).where(Tenant.id == tenant_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting tenant by ID: {e}")
            return None

    def create_access_token(self, user: User) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(
        self,
        user: User,
        device_info: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        """Create and store refresh token."""
        try:
            # Generate secure random token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

            refresh_token = RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expire,
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.db.add(refresh_token)
            await self.db.commit()

            return token

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token",
            )

    async def verify_access_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "access":
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid access token: {e}")
            return None

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str] | None:
        """Refresh access token using refresh token."""
        try:
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

            # Get refresh token from database
            query = (
                select(RefreshToken)
                .options(selectinload(RefreshToken.user).selectinload(User.tenant))
                .where(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > datetime.utcnow(),
                )
            )
            result = await self.db.execute(query)
            db_token = result.scalar_one_or_none()

            if not db_token or not db_token.user.is_active:
                return None

            # Create new tokens
            new_access_token = self.create_access_token(db_token.user)
            new_refresh_token = await self.create_refresh_token(
                db_token.user,
                device_info=db_token.device_info,
                ip_address=db_token.ip_address,
                user_agent=db_token.user_agent,
            )

            # Revoke old refresh token
            db_token.is_revoked = True
            await self.db.commit()

            return new_access_token, new_refresh_token

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token."""
        try:
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

            query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
            result = await self.db.execute(query)
            db_token = result.scalar_one_or_none()

            if db_token:
                db_token.is_revoked = True
                await self.db.commit()
                return True

            return False

        except Exception as e:
            logger.error(f"Error revoking refresh token: {e}")
            return False

    async def revoke_all_user_tokens(self, user_id: UUID) -> bool:
        """Revoke all refresh tokens for a user."""
        try:
            query = select(RefreshToken).where(
                RefreshToken.user_id == user_id, RefreshToken.is_revoked == False
            )
            result = await self.db.execute(query)
            tokens = result.scalars().all()

            for token in tokens:
                token.is_revoked = True

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error revoking user tokens: {e}")
            return False

    async def create_oauth_user(
        self,
        provider: AuthProvider,
        provider_user_id: str,
        provider_email: str,
        provider_data: dict[str, Any],
        tenant_id: UUID,
        full_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        """Create user from OAuth provider."""
        try:
            # Create user
            user = User(
                tenant_id=tenant_id,
                email=provider_email,
                full_name=full_name,
                avatar_url=avatar_url,
                is_verified=True,  # OAuth emails are pre-verified
                role=UserRole.TENANT_USER,
            )

            self.db.add(user)
            await self.db.flush()  # Get user ID

            # Create OAuth provider record
            auth_provider = UserAuthProvider(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
                provider_data=provider_data,
            )

            self.db.add(auth_provider)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Created OAuth user {user.id} from {provider}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating OAuth user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create OAuth user",
            )

    async def get_or_create_oauth_user(
        self,
        provider: AuthProvider,
        provider_user_id: str,
        provider_email: str,
        provider_data: dict[str, Any],
        tenant_id: UUID,
        **kwargs,
    ) -> User:
        """Get existing OAuth user or create new one."""
        try:
            # First, try to find existing OAuth connection
            query = (
                select(UserAuthProvider)
                .options(selectinload(UserAuthProvider.user).selectinload(User.tenant))
                .where(
                    UserAuthProvider.provider == provider,
                    UserAuthProvider.provider_user_id == provider_user_id,
                )
            )
            result = await self.db.execute(query)
            auth_provider = result.scalar_one_or_none()

            if auth_provider and auth_provider.user.tenant_id == tenant_id:
                # Update provider data
                auth_provider.provider_data = provider_data
                auth_provider.updated_at = datetime.now()
                await self.db.commit()
                return auth_provider.user

            # Try to find user by email in the tenant
            existing_user = await self.get_user_by_email(provider_email, tenant_id)
            if existing_user:
                # Link OAuth to existing user
                new_auth_provider = UserAuthProvider(
                    user_id=existing_user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    provider_email=provider_email,
                    provider_data=provider_data,
                )
                self.db.add(new_auth_provider)
                await self.db.commit()
                return existing_user

            # Create new user
            return await self.create_oauth_user(
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
                provider_data=provider_data,
                tenant_id=tenant_id,
                **kwargs,
            )

        except Exception as e:
            logger.error(f"Error getting/creating OAuth user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth authentication failed",
            )

    async def update_user_profile(
        self, user_id: UUID, updates: dict[str, Any]
    ) -> User | None:
        """Update user profile."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            # Update allowed fields
            allowed_fields = {
                "username",
                "full_name",
                "avatar_url",
                "timezone",
                "language",
                "preferences",
            }

            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)

            user.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(user)

            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user profile: {e}")
            return None

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.hashed_password:
                return False

            # Verify old password
            if not bcrypt.checkpw(old_password.encode(), user.hashed_password.encode()):
                return False

            # Hash new password
            new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            user.hashed_password = new_hashed
            user.updated_at = datetime.now()

            # Revoke all refresh tokens (force re-login)
            await self.revoke_all_user_tokens(user_id)

            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error changing password: {e}")
            return False
