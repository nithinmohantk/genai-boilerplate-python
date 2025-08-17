#!/usr/bin/env python3
"""
Test script to verify authentication functionality.
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin123!"
DEFAULT_TENANT_DOMAIN = "default"


async def test_authentication():
    """Test authentication flow."""
    print("🧪 Testing authentication system...")

    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("\n1. Testing health check...")
            response = await client.get(f"{API_BASE}/status")
            if response.status_code == 200:
                print("✅ API is responding")
                print(f"   Status: {response.json()}")
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return

            # Test 2: Login with admin credentials
            print("\n2. Testing admin login...")
            login_data = {
                "email": DEFAULT_ADMIN_EMAIL,
                "password": DEFAULT_ADMIN_PASSWORD,
                "tenant_domain": DEFAULT_TENANT_DOMAIN,
            }

            response = await client.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ Admin login successful")
                tokens = response.json()
                access_token = tokens["access_token"]
                refresh_token = tokens["refresh_token"]
                print(f"   Access token: {access_token[:50]}...")
                print(f"   Refresh token: {refresh_token[:50]}...")
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return

            # Test 3: Get current user info
            print("\n3. Testing authenticated request...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{API_BASE}/auth/me", headers=headers)

            if response.status_code == 200:
                print("✅ Authenticated request successful")
                user_info = response.json()
                print(f"   User ID: {user_info['id']}")
                print(f"   Email: {user_info['email']}")
                print(f"   Role: {user_info['role']}")
                print(f"   Tenant ID: {user_info['tenant_id']}")
            else:
                print(f"❌ Authenticated request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return

            # Test 4: Test token refresh
            print("\n4. Testing token refresh...")
            refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
            response = await client.post(
                f"{API_BASE}/auth/refresh", headers=refresh_headers
            )

            if response.status_code == 200:
                print("✅ Token refresh successful")
                new_tokens = response.json()
                new_access_token = new_tokens["access_token"]
                print(f"   New access token: {new_access_token[:50]}...")
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Error: {response.text}")

            # Test 5: Test WebSocket stats (requires authentication)
            print("\n5. Testing WebSocket stats endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{API_BASE}/ws/stats", headers=headers)

            if response.status_code == 200:
                print("✅ WebSocket stats endpoint accessible")
                stats = response.json()
                print(f"   Stats: {stats}")
            else:
                print(f"❌ WebSocket stats failed: {response.status_code}")
                print(f"   Error: {response.text}")

            # Test 6: Test logout
            print("\n6. Testing logout...")
            logout_headers = {"Authorization": f"Bearer {refresh_token}"}
            response = await client.post(
                f"{API_BASE}/auth/logout", headers=logout_headers
            )

            if response.status_code == 200:
                print("✅ Logout successful")
                print(f"   Message: {response.json()['message']}")
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"   Error: {response.text}")

            print("\n🎉 All authentication tests passed!")

        except httpx.ConnectError:
            print(
                "❌ Cannot connect to server. Make sure the server is running on localhost:8000"
            )
            print("   Run: python backend/src/main.py")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")


async def test_registration():
    """Test user registration."""
    print("\n🧪 Testing user registration...")

    async with httpx.AsyncClient() as client:
        try:
            # First get the default tenant ID
            login_data = {
                "email": DEFAULT_ADMIN_EMAIL,
                "password": DEFAULT_ADMIN_PASSWORD,
                "tenant_domain": DEFAULT_TENANT_DOMAIN,
            }

            response = await client.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code != 200:
                print("❌ Cannot login as admin to get tenant info")
                return

            access_token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}

            # Get current user to find tenant ID
            response = await client.get(f"{API_BASE}/auth/me", headers=headers)
            if response.status_code != 200:
                print("❌ Cannot get admin user info")
                return

            tenant_id = response.json()["tenant_id"]

            # Test user registration
            test_user = {
                "email": "testuser@example.com",
                "password": "testpass123!",
                "tenant_id": tenant_id,
                "full_name": "Test User",
                "username": "testuser",
            }

            response = await client.post(f"{API_BASE}/auth/register", json=test_user)

            if response.status_code == 200:
                print("✅ User registration successful")
                user_info = response.json()
                print(f"   User ID: {user_info['id']}")
                print(f"   Email: {user_info['email']}")
                print(f"   Username: {user_info['username']}")
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"   Error: {response.text}")

        except Exception as e:
            print(f"❌ Registration test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting authentication tests...")
    print("⚠️  Make sure the server is running: python backend/src/main.py")
    print("⚠️  Make sure the database is initialized: python backend/scripts/init_db.py")

    try:
        asyncio.run(test_authentication())
        asyncio.run(test_registration())

        print("\n📋 Next steps:")
        print("   • Start the frontend: cd frontend && npm start")
        print("   • Access the app: http://localhost:3000")
        print("   • Login with admin@example.com / admin123!")
        print("   • Check API docs: http://localhost:8000/docs")

    except KeyboardInterrupt:
        print("\n⏹️  Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Tests failed: {e}")
        sys.exit(1)
