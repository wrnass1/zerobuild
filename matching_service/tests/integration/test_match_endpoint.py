import httpx
import respx


async def test_match_endpoint_requires_auth(client: httpx.AsyncClient):
    r = await client.get("/match/1")
    assert r.status_code in (401, 403)


@respx.mock
async def test_match_endpoint_happy_path(client: httpx.AsyncClient, auth_header: dict):
    # Mock upstream Idea + Auth services
    respx.get("http://ideas.test/ideas/10").respond(
        200,
        json={
            "id": 10,
            "required_stack": ["Python", "FastAPI"],
            "complexity": "low",
        },
    )
    respx.get("http://auth.test/profiles").respond(
        200,
        json=[
            {"id": 1, "name": "A", "tech_stack": ["Python"], "level": "junior", "projects": []},
            {"id": 2, "name": "B", "tech_stack": ["Go"], "level": "junior", "projects": []},
        ],
    )

    r = await client.get("/match/10?limit=10", headers=auth_header)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["idea_id"] == 10
    assert len(data["matches"]) == 2
    # Первый кандидат должен иметь больший скор из-за пересечения стека.
    assert data["matches"][0]["candidate_id"] == 1
    assert data["matches"][0]["score"] >= data["matches"][1]["score"]

