import httpx


async def test_list_ideas_empty(client: httpx.AsyncClient):
    r = await client.get("/ideas")
    assert r.status_code == 200
    assert r.json() == []


async def test_create_update_delete_idea(client: httpx.AsyncClient, auth_header: dict):
    # create
    r = await client.post(
        "/ideas",
        headers=auth_header,
        json={
            "title": "My Idea",
            "description": "Desc",
            "required_stack": ["Python", "FastAPI"],
            "complexity": "low",
            "participants_count": 2,
            "status": "open",
        },
    )
    assert r.status_code == 201, r.text
    idea = r.json()
    idea_id = idea["id"]
    assert idea["owner_id"] == 1

    # get
    r = await client.get(f"/ideas/{idea_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "My Idea"

    # update (title)
    r = await client.put(
        f"/ideas/{idea_id}",
        headers=auth_header,
        json={"title": "Updated"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Updated"

    # delete
    r = await client.delete(f"/ideas/{idea_id}", headers=auth_header)
    assert r.status_code == 204, r.text

    # get -> 404
    r = await client.get(f"/ideas/{idea_id}")
    assert r.status_code == 404


async def test_create_requires_auth(client: httpx.AsyncClient):
    r = await client.post("/ideas", json={"title": "x", "required_stack": []})
    assert r.status_code in (401, 403)

