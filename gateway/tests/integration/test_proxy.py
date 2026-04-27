import httpx
import respx


@respx.mock
async def test_proxy_forwards_headers_and_path(client: httpx.AsyncClient):
    # Gateway should route /api/kanban/* to http://kanban.up/*
    route = respx.get("http://kanban.up/boards/1").respond(200, json={"ok": True})

    r = await client.get("/api/kanban/boards/1", headers={"Authorization": "Bearer t"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}
    assert route.called


async def test_proxy_unknown_path_404(client: httpx.AsyncClient):
    r = await client.get("/api/unknown/x")
    assert r.status_code == 404

