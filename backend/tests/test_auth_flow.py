import asyncio
import httpx
import sys

async def test_auth_flow():
    base_url = "http://127.0.0.1:8000"
    async with httpx.AsyncClient(base_url=base_url) as ac:
        print("1. Login")
        login_data = {
            "username": "user@example.com",
            "password": "password"
        }
        response = await ac.post("/api/v1/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            sys.exit(1)

        data = response.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        print(f"Login success. Access: {access_token[:10]}...")

        # Check cookie
        # httpx client stores cookies automatically
        cookies = ac.cookies
        if "refresh_token" not in cookies:
             # Look in response cookies explicitly
             if "refresh_token" in response.cookies:
                 print("Refresh token found in response cookies")
             else:
                 print("Refresh token NOT found in cookies")
                 sys.exit(1)

        print("2. Get Me")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await ac.get("/api/v1/auth/me", headers=headers)
        if response.status_code != 200:
            print(f"Get Me failed: {response.text}")
            sys.exit(1)
        user_data = response.json()
        print(f"User: {user_data['email']}, Role: {user_data['role']}")

        print("3. Refresh Token")
        # Ensure we wait a bit to ensure 'exp' might change if we were checking that,
        # but we are just checking new token generation.
        # We need to send the cookie. httpx AsyncClient persists cookies.
        response = await ac.post("/api/v1/auth/refresh")
        if response.status_code != 200:
            print(f"Refresh failed: {response.text}")
            sys.exit(1)

        data = response.json()
        new_access_token = data["access_token"]
        print(f"New Access Token: {new_access_token[:10]}...")

        if new_access_token == access_token:
            print("Warning: Access token didn't change (might be same if exp is same second? No, new generation usually different signature due to time)")

        print("4. Verify new token works")
        headers = {"Authorization": f"Bearer {new_access_token}"}
        response = await ac.get("/api/v1/auth/me", headers=headers)
        if response.status_code != 200:
             print(f"Get Me with new token failed: {response.text}")
             sys.exit(1)

        print("5. Logout")
        response = await ac.post("/api/v1/auth/logout")
        if response.status_code != 200:
            print(f"Logout failed: {response.text}")
            sys.exit(1)

        print("6. Refresh should fail")
        response = await ac.post("/api/v1/auth/refresh")
        if response.status_code != 401:
             print(f"Refresh succeeded after logout? Status: {response.status_code}")
             sys.exit(1)

    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
