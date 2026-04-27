import httpx


async def test_register_login_and_profile(client: httpx.AsyncClient):
    # register
    r = await client.post(
        "/register",
        json={"email": "a@example.com", "password": "pass123", "name": "Alice"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token

    # profile (authorized)
    r = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "a@example.com"

    # login
    r = await client.post("/login", json={"email": "a@example.com", "password": "pass123"})
    assert r.status_code == 200, r.text
    token2 = r.json()["access_token"]
    assert token2


async def test_profile_requires_auth(client: httpx.AsyncClient):
    r = await client.get("/profile")
    assert r.status_code == 403 or r.status_code == 401


async def test_register_duplicate_email_returns_400(client: httpx.AsyncClient):
    payload = {"email": "dup@example.com", "password": "pass123", "name": "Dup"}
    r1 = await client.post("/register", json=payload)
    assert r1.status_code == 200, r1.text

    r2 = await client.post("/register", json=payload)
    assert r2.status_code == 400, r2.text

