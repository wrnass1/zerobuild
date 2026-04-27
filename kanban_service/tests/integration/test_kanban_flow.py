import httpx


async def test_create_board_and_get_board(client: httpx.AsyncClient, auth_header: dict):
    r = await client.post(
        "/boards",
        headers=auth_header,
        json={"name": "Board 1", "project_id": 123, "idea_id": 10},
    )
    assert r.status_code == 201, r.text
    board = r.json()
    board_id = board["id"]

    r = await client.get(f"/boards/{board_id}", headers=auth_header)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["id"] == board_id
    assert len(data["columns"]) == 3


async def test_create_task_get_and_update_task(client: httpx.AsyncClient, auth_header: dict):
    # create board first
    r = await client.post("/boards", headers=auth_header, json={"name": "Board 2"})
    assert r.status_code == 201, r.text
    board_id = r.json()["id"]

    # fetch board to get a column id
    r = await client.get(f"/boards/{board_id}", headers=auth_header)
    assert r.status_code == 200
    column_id = r.json()["columns"][0]["id"]

    # create task
    r = await client.post(
        "/tasks",
        headers=auth_header,
        json={
            "board_id": board_id,
            "column_id": column_id,
            "title": "Task 1",
            "description": "Desc",
        },
    )
    assert r.status_code == 201, r.text
    task_id = r.json()["id"]

    # get task
    r = await client.get(f"/tasks/{task_id}", headers=auth_header)
    assert r.status_code == 200
    assert r.json()["title"] == "Task 1"

    # update task
    r = await client.put(f"/tasks/{task_id}", headers=auth_header, json={"title": "Task 1 updated"})
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Task 1 updated"


async def test_endpoints_require_auth(client: httpx.AsyncClient):
    r = await client.get("/boards/1")
    assert r.status_code in (401, 403)

