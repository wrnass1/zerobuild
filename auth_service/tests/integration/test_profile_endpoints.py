import httpx


async def _register_and_get_token(client: httpx.AsyncClient, *, email: str = "u@example.com") -> str:
    r = await client.post(
        "/register",
        json={"email": email, "password": "pass123", "name": "User"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token
    return token


async def test_update_profile_put_profile(client: httpx.AsyncClient):
    token = await _register_and_get_token(client, email="upd@example.com")

    r = await client.put(
        "/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Name",
            "level": "middle",
            "description": "About me",
            "tech_stack": ["Python", "FastAPI"],
            "projects": [{"name": "proj1"}],
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["name"] == "Updated Name"
    assert data["level"] == "middle"
    assert data["tech_stack"] == ["Python", "FastAPI"]
    assert isinstance(data["projects"], list)


async def test_profiles_internal_endpoints(client: httpx.AsyncClient):
    token = await _register_and_get_token(client, email="p1@example.com")
    _ = await _register_and_get_token(client, email="p2@example.com")

    # GET /profiles returns list
    r = await client.get("/profiles")
    assert r.status_code == 200, r.text
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 2

    # GET /profiles/{id} returns single profile (use current user's id from /profile)
    me = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    my_id = me.json()["id"]

    r = await client.get(f"/profiles/{my_id}")
    assert r.status_code == 200, r.text
    assert r.json()["id"] == my_id


async def test_delete_profile_removes_user(client: httpx.AsyncClient):
    token = await _register_and_get_token(client, email="del@example.com")

    r = await client.delete("/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204, r.text

    # profile now should be 404 (user removed)
    r = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404, r.text

