#!/usr/bin/env python3
"""
Database initialization script.
Creates default tenant and admin user for initial setup.
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from core.database import close_db, init_db
from core.database import get_async_session
from models.auth import TenantStatus, UserRole
from services.auth_service import AuthService

DEFAULT_TENANT_DOMAIN = "default"
DEFAULT_TENANT_NAME = "Default Organization"
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin123!"


async def create_default_data():
    """Create default tenant and admin user."""
    print("🗄️  Initializing database...")

    # Initialize database
    await init_db()

    print("📊 Creating default tenant and admin user...")

    async with get_async_session() as db:
        auth_service = AuthService(db)

        try:
            # Check if default tenant already exists
            existing_tenant = await auth_service.get_tenant_by_domain(
                DEFAULT_TENANT_DOMAIN
            )

            if existing_tenant:
                print(f"✅ Default tenant already exists: {DEFAULT_TENANT_DOMAIN}")
                tenant = existing_tenant
            else:
                # Create default tenant
                tenant = await auth_service.create_tenant(
                    name=DEFAULT_TENANT_NAME,
                    domain=DEFAULT_TENANT_DOMAIN,
                    status=TenantStatus.ACTIVE,
                    settings={
                        "allow_registration": True,
                        "max_users": 1000,
                        "features": ["chat", "documents", "api_access"],
                    },
                    branding={
                        "primary_color": "#1976d2",
                        "logo_url": None,
                        "company_name": DEFAULT_TENANT_NAME,
                    },
                )
                print(f"✅ Created default tenant: {tenant.domain}")

            # Check if admin user already exists
            existing_admin = await auth_service.get_user_by_email(
                DEFAULT_ADMIN_EMAIL, tenant.id
            )

            if existing_admin:
                print(f"✅ Default admin user already exists: {DEFAULT_ADMIN_EMAIL}")
            else:
                # Create admin user
                admin_user = await auth_service.create_user(
                    email=DEFAULT_ADMIN_EMAIL,
                    password=DEFAULT_ADMIN_PASSWORD,
                    tenant_id=tenant.id,
                    full_name="System Administrator",
                    role=UserRole.SUPER_ADMIN,
                    is_verified=True,  # Pre-verified for admin
                )
                print(f"✅ Created admin user: {admin_user.email}")
                print(f"🔐 Admin password: {DEFAULT_ADMIN_PASSWORD}")

            print("\n🎉 Database initialization completed successfully!")
            print("\n📋 Summary:")
            print(f"   • Tenant Domain: {tenant.domain}")
            print(f"   • Tenant ID: {tenant.id}")
            print(f"   • Admin Email: {DEFAULT_ADMIN_EMAIL}")
            print(f"   • Admin Password: {DEFAULT_ADMIN_PASSWORD}")
            print("   • Login URL: http://localhost:8000/api/v1/auth/login")
            print("   • API Docs: http://localhost:8000/docs")

        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            raise

        pass  # Session will be closed automatically

    # Close database connections
    await close_db()


if __name__ == "__main__":
    print("🚀 Starting database initialization...")

    try:
        asyncio.run(create_default_data())
    except KeyboardInterrupt:
        print("\n⏹️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Initialization failed: {e}")
        sys.exit(1)
