"""
Admin API endpoints for tenant and user management.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user, CurrentUser, require_super_admin, require_tenant_admin
from database.session import get_db
from models.auth import (
    User, Tenant, TenantApiKey, RefreshToken,
    UserRole, TenantStatus,
    UserResponse, TenantResponse, ApiKeyResponse,
    TenantCreate, TenantUpdate, UserCreate, UserUpdate, ApiKeyCreate
)
from models.chat import ChatSession, ChatMessage
from services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()


# Tenant Management (Super Admin only)

@router.get("/tenants", response_model=List[TenantResponse])
async def get_all_tenants(
    current_user: CurrentUser = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[TenantStatus] = Query(None, alias="status")
):
    """Get all tenants (Super admin only)."""
    try:
        query = (
            select(Tenant)
            .order_by(desc(Tenant.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        if status_filter:
            query = query.where(Tenant.status == status_filter)
        
        result = await db.execute(query)
        tenants = result.scalars().all()
        
        return [TenantResponse.from_orm(tenant) for tenant in tenants]
    
    except Exception as e:
        logger.error(f"Error getting tenants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenants"
        )


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant_admin(
    tenant_data: TenantCreate,
    current_user: CurrentUser = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tenant (Super admin only)."""
    try:
        auth_service = AuthService(db)
        
        # Check if domain already exists
        existing_tenant = await auth_service.get_tenant_by_domain(tenant_data.domain)
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant domain already exists"
            )
        
        tenant = await auth_service.create_tenant(
            name=tenant_data.name,
            domain=tenant_data.domain,
            created_by=current_user.user_id,
            status=tenant_data.status,
            settings=tenant_data.settings,
            branding=tenant_data.branding,
            limits=tenant_data.limits
        )
        
        logger.info(f"Tenant created: {tenant.id} by super admin {current_user.user_id}")
        
        return TenantResponse.from_orm(tenant)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant"
        )


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant_admin(
    tenant_id: UUID,
    tenant_updates: TenantUpdate,
    current_user: CurrentUser = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a tenant (Super admin only)."""
    try:
        auth_service = AuthService(db)
        
        tenant = await auth_service.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Update tenant
        update_data = tenant_updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(tenant, field):
                setattr(tenant, field, value)
        
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Tenant updated: {tenant_id} by super admin {current_user.user_id}")
        
        return TenantResponse.from_orm(tenant)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant"
        )


@router.get("/tenants/{tenant_id}/stats")
async def get_tenant_stats(
    tenant_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant statistics."""
    # Super admins can see any tenant, tenant admins can see their own
    if not current_user.is_super_admin:
        if current_user.tenant_id != tenant_id or not current_user.is_tenant_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Get user count
        user_count_query = (
            select(func.count(User.id))
            .where(User.tenant_id == tenant_id)
        )
        user_count_result = await db.execute(user_count_query)
        user_count = user_count_result.scalar() or 0
        
        # Get active user count
        active_user_count_query = (
            select(func.count(User.id))
            .where(User.tenant_id == tenant_id, User.is_active == True)
        )
        active_user_count_result = await db.execute(active_user_count_query)
        active_user_count = active_user_count_result.scalar() or 0
        
        # Get session count
        session_count_query = (
            select(func.count(ChatSession.id))
            .where(ChatSession.tenant_id == tenant_id)
        )
        session_count_result = await db.execute(session_count_query)
        session_count = session_count_result.scalar() or 0
        
        # Get message count
        message_count_query = (
            select(func.count(ChatMessage.id))
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .where(ChatSession.tenant_id == tenant_id)
        )
        message_count_result = await db.execute(message_count_query)
        message_count = message_count_result.scalar() or 0
        
        # Get API key count
        api_key_count_query = (
            select(func.count(TenantApiKey.id))
            .where(TenantApiKey.tenant_id == tenant_id, TenantApiKey.is_active == True)
        )
        api_key_count_result = await db.execute(api_key_count_query)
        api_key_count = api_key_count_result.scalar() or 0
        
        return {
            "status": "success",
            "data": {
                "tenant_id": tenant_id,
                "users": {
                    "total": user_count,
                    "active": active_user_count,
                    "inactive": user_count - active_user_count
                },
                "chat": {
                    "sessions": session_count,
                    "messages": message_count,
                    "avg_messages_per_session": message_count / session_count if session_count > 0 else 0
                },
                "api_keys": api_key_count
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting tenant stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant statistics"
        )


# User Management

@router.get("/users", response_model=List[UserResponse])
async def get_tenant_users(
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    role_filter: Optional[UserRole] = Query(None, alias="role"),
    active_only: Optional[bool] = Query(None)
):
    """Get users in the current tenant."""
    try:
        query = (
            select(User)
            .where(User.tenant_id == current_user.tenant_id)
            .order_by(desc(User.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        if role_filter:
            query = query.where(User.role == role_filter)
        
        if active_only is not None:
            query = query.where(User.is_active == active_only)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [UserResponse.from_orm(user) for user in users]
    
    except Exception as e:
        logger.error(f"Error getting tenant users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@router.post("/users", response_model=UserResponse)
async def create_user_admin(
    user_data: UserCreate,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user in the current tenant."""
    try:
        auth_service = AuthService(db)
        
        # Force tenant ID to current user's tenant
        user_data.tenant_id = current_user.tenant_id
        
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(
            user_data.email,
            current_user.tenant_id
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Only super admins can create other admins
        if user_data.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            if not current_user.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to create admin users"
                )
        
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            tenant_id=current_user.tenant_id,
            username=user_data.username,
            full_name=user_data.full_name,
            role=user_data.role,
            timezone=user_data.timezone,
            language=user_data.language,
            preferences=user_data.preferences
        )
        
        logger.info(f"User created: {user.id} by admin {current_user.user_id}")
        
        return UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_updates: UserUpdate,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a user in the current tenant."""
    try:
        auth_service = AuthService(db)
        
        # Get user and verify they belong to the current tenant
        user = await auth_service.get_user_by_id(user_id)
        if not user or user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only super admins can modify admin users
        if user.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            if not current_user.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to modify admin users"
                )
        
        # Update user
        updated_user = await auth_service.update_user_profile(
            user_id=user_id,
            updates=user_updates.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated: {user_id} by admin {current_user.user_id}")
        
        return UserResponse.from_orm(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user."""
    try:
        auth_service = AuthService(db)
        
        # Get user and verify they belong to the current tenant
        user = await auth_service.get_user_by_id(user_id)
        if not user or user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cannot deactivate self
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself"
            )
        
        # Only super admins can deactivate admin users
        if user.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            if not current_user.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to deactivate admin users"
                )
        
        # Deactivate user
        user.is_active = False
        await db.commit()
        
        # Revoke all user tokens
        await auth_service.revoke_all_user_tokens(user_id)
        
        logger.info(f"User deactivated: {user_id} by admin {current_user.user_id}")
        
        return {"message": "User deactivated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deactivating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Activate a user."""
    try:
        auth_service = AuthService(db)
        
        # Get user and verify they belong to the current tenant
        user = await auth_service.get_user_by_id(user_id)
        if not user or user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Activate user
        user.is_active = True
        await db.commit()
        
        logger.info(f"User activated: {user_id} by admin {current_user.user_id}")
        
        return {"message": "User activated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error activating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


# API Key Management

@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def get_tenant_api_keys(
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get API keys for the current tenant."""
    try:
        query = (
            select(TenantApiKey)
            .where(TenantApiKey.tenant_id == current_user.tenant_id)
            .order_by(desc(TenantApiKey.created_at))
        )
        
        result = await db.execute(query)
        api_keys = result.scalars().all()
        
        return [ApiKeyResponse.from_orm(key) for key in api_keys]
    
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys"
        )


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key for the current tenant."""
    try:
        import hashlib
        
        # Hash the API key
        key_hash = hashlib.sha256(key_data.api_key.encode()).hexdigest()
        key_prefix = key_data.api_key[:8]  # First 8 characters for identification
        
        # Check if key name already exists
        existing_key_query = (
            select(TenantApiKey)
            .where(
                TenantApiKey.tenant_id == current_user.tenant_id,
                TenantApiKey.name == key_data.name
            )
        )
        existing_result = await db.execute(existing_key_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key name already exists"
            )
        
        # Create API key
        api_key = TenantApiKey(
            tenant_id=current_user.tenant_id,
            name=key_data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            provider=key_data.provider,
            usage_limits=key_data.usage_limits,
            created_by=current_user.user_id
        )
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        logger.info(f"API key created: {api_key.id} by admin {current_user.user_id}")
        
        return ApiKeyResponse.from_orm(api_key)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: UUID,
    current_user: CurrentUser = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key."""
    try:
        # Get API key and verify it belongs to current tenant
        query = (
            select(TenantApiKey)
            .where(
                TenantApiKey.id == key_id,
                TenantApiKey.tenant_id == current_user.tenant_id
            )
        )
        result = await db.execute(query)
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        await db.delete(api_key)
        await db.commit()
        
        logger.info(f"API key deleted: {key_id} by admin {current_user.user_id}")
        
        return {"message": "API key deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )


# System Monitoring (Super Admin only)

@router.get("/system/stats")
async def get_system_stats(
    current_user: CurrentUser = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics."""
    try:
        # Get tenant count
        tenant_count_query = select(func.count(Tenant.id))
        tenant_count_result = await db.execute(tenant_count_query)
        tenant_count = tenant_count_result.scalar() or 0
        
        # Get user count
        user_count_query = select(func.count(User.id))
        user_count_result = await db.execute(user_count_query)
        user_count = user_count_result.scalar() or 0
        
        # Get active sessions count
        active_sessions_query = select(func.count(ChatSession.id))
        active_sessions_result = await db.execute(active_sessions_query)
        active_sessions = active_sessions_result.scalar() or 0
        
        # Get total messages count
        message_count_query = select(func.count(ChatMessage.id))
        message_count_result = await db.execute(message_count_query)
        message_count = message_count_result.scalar() or 0
        
        # Get active tokens count
        active_tokens_query = (
            select(func.count(RefreshToken.id))
            .where(RefreshToken.is_revoked == False)
        )
        active_tokens_result = await db.execute(active_tokens_query)
        active_tokens = active_tokens_result.scalar() or 0
        
        return {
            "status": "success",
            "data": {
                "tenants": tenant_count,
                "users": user_count,
                "chat_sessions": active_sessions,
                "messages": message_count,
                "active_tokens": active_tokens
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system statistics"
        )
